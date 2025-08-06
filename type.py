import os
import sys
import time
import json
import itertools
import threading
from typing import Protocol, Optional, Union, TextIO

from model import AiAnalysis, CacheData
from openai import OpenAI

# Constants
_THREAD_TIME_OUT = 0.5  # seconds for spinner thread to stop gracefully

# Cache settings
_CACHE_DIR = os.path.join(os.getcwd(), ".tracer_cache")  # Local to project directory
_CACHE_TTL = 86400  # Time-to-live in seconds (24 hours)

# API configuration
_DEFAULT_BASE_URL = f"https://api.openai.com/v1"
_DEFAULT_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
_DEFAULT_MODEL = "gpt-3.5-turbo"
_DEFAULT_TIMEOUT = 30  # seconds
_TEMPERATURE = 0.3  # Controls randomness in AI responses


class PrinterInterface(Protocol):
    """
    Interface for printing messages with verbosity control.
    """

    def print(self, message: str, verbosity: int = 1) -> None:
        """
        Print a message with verbosity control.

        Args:
            message: The message to print
            verbosity: The minimum verbosity level required to print this message
        """
        pass


# interfaces
class AnalysisGetterInterface(Protocol):
    """Interface for getting AI-powered analysis."""

    def get_analysis(self, system_prompt: str, user_prompt: str) -> AiAnalysis:
        """
        Get AI-powered analysis for the provided error data.

        Args:
            system_prompt: System prompt for AI context
            user_prompt: User prompt for AI analysis

        Returns:
            Dictionary with explanation and suggested fix
        """
        pass


class CacheInterface(Protocol):
    """Interface for caching functionality."""

    def set(self, key: str, value: CacheData) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
        """
        pass

    def get(self, key: str) -> Union[CacheData, None]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found
        """
        pass


class TimerInterface(Protocol):
    """
    Interface for timing operations.
    """

    def elapsed(self) -> float:
        """
        Get elapsed time since the timer was started.

        Returns:
            Elapsed time in seconds
        """
        pass


class ProgressIndicatorInterface(Protocol):
    def start(self) -> None:
        """
        Start a spinner animation in a separate thread.
        """
        pass

    def stop(self) -> None:
        """
        Stop the spinner animation.
        """
        pass


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CacheConfig:
    """Configuration for cache settings."""

    def __init__(self):
        self.ttl: int = _CACHE_TTL  # Time-to-live for cache entries in seconds
        self.use_cache: bool = True  # Whether to use caching for AI responses

    def configure(self, cache_ttl=None, use_cache=None) -> None:
        """Configure the cache settings."""
        if cache_ttl is not None:
            self.ttl = cache_ttl
        if use_cache is not None:
            self.use_cache = use_cache


class AIConfig:
    """Configuration for AI integration."""

    def __init__(self):
        self.api_key: Optional[str] = None  # OpenAI API key
        self.api_endpoint: str = _DEFAULT_API_ENDPOINT  # Default API endpoint for AI requests
        self.model: str = _DEFAULT_MODEL  # Default AI model to use
        self.timeout: float = _DEFAULT_TIMEOUT  # Timeout for AI requests in seconds
        self.enabled: bool = False  # Whether AI integration is enabled
        self.use_cache: bool = True  # Whether to use caching for AI responses
        self.base_url: Optional[str] = _DEFAULT_BASE_URL  # Base URL for the AI API

    def configure(
            self,
            api_key=None,
            base_url=None,
            api_endpoint=None,
            model=None,
            timeout=None,
            enabled=None,
            use_cache=None,
    ) -> None:
        """Configure the AI settings."""
        if api_key is not None:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url
        if api_endpoint is not None:
            self.api_endpoint = api_endpoint
        if model is not None:
            self.model = model
        if timeout is not None:
            self.timeout = timeout
        if enabled is not None:
            self.enabled = enabled
        if use_cache is not None:
            self.use_cache = use_cache


class AIClient(AnalysisGetterInterface):
    """Client for making API requests to the AI service."""

    def __init__(self, config: AIConfig):
        self.config = config
        self._schema = AiAnalysis.model_json_schema()
        self._ai_client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)

    def get_analysis(self, system_prompt: str, user_prompt: str) -> AiAnalysis:
        """
        Get AI-powered analysis for the provided error data.

        Args:
            system_prompt: System prompt for AI context
            user_prompt: User prompt for AI analysis

        Returns:
            AiAnalysis object with explanation and suggested fix
        """
        if not self.config.api_key:
            raise ValueError("API key is not set.")

        if not self.config.enabled:
            return AiAnalysis(
                explanation="AI integration is disabled.",
                suggested_fix="Enable AI integration to get analysis."
            )

        self._schema["additionalProperties"] = False

        response = self._ai_client.chat.completions.create(
            model=self.config.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=_TEMPERATURE,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "AiAnalysis",
                    "description": "AI analysis response",
                    "schema": self._schema,
                    "strict": True,
                },
            },
            timeout=self.config.timeout,
        )

        return AiAnalysis.model_validate(json.loads(response.choices[0].message.content))


class FileBasedCache(CacheInterface):
    """File-based cache implementation for storing AI responses."""

    def __init__(self, config: CacheConfig, cache_dir: str = _CACHE_DIR):
        self._cache_dir = cache_dir
        self._ttl = config.ttl  # Time-to-live for cache entries in seconds
        self.use_cache = config.use_cache  # Whether to use caching for AI responses

        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def set(self, key: str, value: CacheData) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
        """
        cache_file = os.path.join(self._cache_dir, f"{key}.json")
        with open(cache_file, 'w') as f:
            json.dump(value.model_dump(), f)

    def get(self, key: str) -> Union[CacheData, None]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found or expired
        """
        cache_file = os.path.join(self._cache_dir, f"{key}.json")
        if not os.path.exists(cache_file):
            return None

        with open(cache_file, 'r') as f:
            data = CacheData.model_validate(json.load(f))

        if time.time() - data.timestamp > self._ttl:
            os.remove(cache_file)

        return data if time.time() - data.timestamp <= self._ttl else None


class Timer(TimerInterface):
    """
    Timer for measuring elapsed time with context manager support.
    """

    def __init__(self, auto_print: bool = True, message: str = "Operation completed in"):
        """
        Initialize the timer.

        Args:
            auto_print: Whether to automatically print the elapsed time on exit
            message: Message to print before the elapsed time
        """
        self._start_time: float = 0.0
        self._elapsed: float = 0.0
        self._running: bool = False
        self._auto_print: bool = auto_print
        self._message: str = message

    def __enter__(self) -> 'Timer':
        """
        Start the timer when entering the context.

        Returns:
            The timer instance
        """
        self._start_time = time.time()
        self._running = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stop the timer when exiting the context.
        """
        self._elapsed = self.elapsed()
        self._running = False

        if self._auto_print:
            print(f"{Colors.CYAN}{self._message} {self._elapsed:.2f}s{Colors.ENDC}")

    def elapsed(self) -> float:
        """
        Get elapsed time since the timer was started.

        Returns:
            Elapsed time in seconds
        """
        if self._running:
            return time.time() - self._start_time
        return self._elapsed


class ConsolePrinter(PrinterInterface):
    """
    Default printer implementation that prints to the console.
    """

    def __init__(self, verbosity: int = 2):
        """
        Initialize the printer with a verbosity level.

        Args:
            verbosity: The verbosity level (0=minimal, 1=normal, 2=detailed)
        """
        self.verbosity: int = verbosity

    def print(self, message: str, verbosity: int = 1) -> None:
        """
        Print a message if the verbosity level is high enough.

        Args:
            message: The message to print
            verbosity: The minimum verbosity level required to print this message
        """
        if self.verbosity >= verbosity:
            print(message, end="")


class NoOpPrinter(PrinterInterface):
    """
    Default printer implementation that prints to the console.
    """

    def __init__(self):
        pass

    def print(self, message: str, verbosity: int = 1) -> None:
        pass


class NoOpProgressIndicator(ProgressIndicatorInterface):
    """No-op progress indicator that does nothing."""

    def __init__(self):
        """Initialize the no-op progress indicator."""
        pass

    def start(self) -> None:
        """Start the no-op progress indicator (does nothing)."""
        pass

    def stop(self) -> None:
        """Stop the no-op progress indicator (does nothing)."""
        pass


class Spinner(ProgressIndicatorInterface):
    """Spinner animation for indicating progress in a separate thread."""

    def __init__(self, stop_event: threading.Event, output: TextIO = sys.stdout, message: str = "Processing"):
        """
        Initialize the spinner with a stop event and output stream.
        Args:
            stop_event: Threading event to signal when to stop the spinner
            output: Output stream (default: sys.stdout)
            message: Message to display next to the spinner
        """
        self._spinner_thread: Optional[threading.Thread] = None
        self._stop_event: threading.Event = stop_event if stop_event else threading.Event()
        self._output: TextIO = output
        self._message: str = message
        self._sleep: float = 0.1

    def _spin_worker(self):
        spinner = itertools.cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        start_time = time.time()
        while not self._stop_event.is_set():
            elapsed = time.time() - start_time
            self._output.write(f"\r{Colors.CYAN}{self._message} {next(spinner)} {elapsed:.1f}s{Colors.ENDC}")
            self._output.flush()
            time.sleep(self._sleep)

    def _clear_line(self) -> None:
        """
        Clear the current line in the terminal.
        """
        self._output.write("\r" + " " * 80 + "\r")
        self._output.flush()

    def start(self) -> None:
        """
        Start a spinner animation in a separate thread.
        """
        self._spinner_thread = threading.Thread(target=self._spin_worker)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()

    def stop(self) -> None:
        """
        Stop the spinner animation.
        """
        if self._spinner_thread and self._spinner_thread.is_alive():
            self._stop_event.set()
            self._spinner_thread.join(_THREAD_TIME_OUT)

        self._clear_line()
