"""
etracer: Enhanced Python tracer with AI-powered error analysis
"""

import hashlib
import json
import linecache
import os
import sys
import threading
import time
from types import TracebackType
from typing import Any, Callable, List, Optional, Type, Union

from .interfaces import (
    AnalysisGetterInterface,
    CacheInterface,
    PrinterInterface,
    ProgressIndicatorInterface,
)
from .models import AiAnalysis, CacheData, DataForAnalysis, Frame
from .utils import (
    AIClient,
    AIConfig,
    CacheConfig,
    Colors,
    ConsolePrinter,
    FileBasedCache,
    Spinner,
    Timer,
)

# Constants
_MAX_STR_LEN = 100


class Tracer:
    """Main tracer class that handles exception interception and formatting."""

    def __init__(
        self,
        ai_client: Optional[AnalysisGetterInterface] = None,
        printer: Optional[PrinterInterface] = None,
        cache: Optional[CacheInterface] = None,
        progress_indicator: Optional[ProgressIndicatorInterface] = None,
    ):
        # Store the original excepthook
        self.original_excepthook = sys.excepthook
        self.enabled: bool = False  # Whether the tracer is currently enabled
        self.verbosity: int = 2  # Default verbosity level (0=minimal, 1=normal, 2=detailed)
        self.show_locals: bool = (
            True if self.verbosity == 2 else False
        )  # Show local variables if verbosity is high
        self._ai_analysis_failed: bool = True  # Flag to track AI analysis failure
        self.ai_config = AIConfig()  # AI integration configuration
        self._traceback_frames: List[Frame] = []  # Store traceback frames for analysis
        self._data_for_analysis: Optional[DataForAnalysis] = None  # Store data for AI analysis
        self._system_prompt: str = """
        You are an expert Python developer helping with debugging.
        Provide clear, concise explanations of errors and practical suggestions for fixing them.
        """
        # Initialize components as None for lazy loading
        self._ai_client: Optional[AnalysisGetterInterface] = ai_client
        self._cache: Optional[CacheInterface] = (
            cache if cache is not None else FileBasedCache(CacheConfig())
        )
        self._progress_indicator: Optional[ProgressIndicatorInterface] = (
            progress_indicator
            if progress_indicator is not None
            else Spinner(
                stop_event=threading.Event(),
                message="AI Analysis running...",
            )
        )
        self._printer: PrinterInterface = (
            printer if printer is not None else ConsolePrinter(verbosity=self.verbosity)
        )

    def analyze_exception(self, exception: Exception) -> None:
        """
        Explicitly analyze an exception that's been caught.

        Args:
            exception: The caught exception
        """
        if not self.enabled:
            self.original_excepthook(type(exception), exception, exception.__traceback__)
            return

        self._format_exception(type(exception), exception, exception.__traceback__)

    def analyze(self, func: Callable) -> Callable:
        """
        Decorator to catch and format exceptions in a function.

        Args:
            func: The function to decorate

        Returns:
            Wrapped function with exception handling
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.analyze_exception(e)

        return wrapper

    def analyzer(self) -> Any:
        """Context manager to catch and format exceptions."""

        class ExceptionAnalyzer:
            def __init__(self, tracer: "Tracer") -> None:
                self.tracer = tracer

            def __enter__(self) -> "ExceptionAnalyzer":
                return self

            def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> bool:
                if exc_type is not None:
                    self.tracer.exception_handler(exc_type, exc_value, exc_traceback)
                    return True  # Suppress the exception
                return False

        return ExceptionAnalyzer(self)

    def enable(
        self,
        verbosity: int = 2,
        enable_ai: bool = False,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        """
        Enable the tracer by replacing the default excepthook.

        Args:
            verbosity: How much detail to show (0=minimal, 1=normal, 2=detailed)
            enable_ai: Whether to use AI for error analysis
            api_key: API key for AI analysis
            model: AI model to use for analysis
            base_url: Base URL for the AI API
        """
        if not self.enabled:
            sys.excepthook = self.exception_handler
            self.enabled = True
            self.verbosity = verbosity if verbosity in (0, 1, 2) else 2
            self.show_locals = True if self.verbosity == 2 else False

            # Update printer's verbosity level
            if hasattr(self._printer, "set_verbosity"):
                self._printer.set_verbosity(self.verbosity)

            if enable_ai:
                self.ai_config.configure(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    enabled=enable_ai,
                    use_cache=True if enable_ai else False,
                )
                if self._ai_client is None:
                    self._ai_client = AIClient(config=self.ai_config)
                self._printer.print(
                    f"{Colors.GREEN}Tracer enabled: Enhanced stack traces with AI analysis"
                    f" activated{Colors.ENDC}\n"
                )
            else:
                self._printer.print(
                    f"{Colors.GREEN}Tracer enabled: Enhanced stack traces activated"
                    f" (AI disabled){Colors.ENDC}\n"
                )

    def disable(self) -> None:
        """Disable the tracer and restore the original excepthook."""
        if self.enabled:
            sys.excepthook = self.original_excepthook
            self.enabled = False
            self._printer.print(
                f"{Colors.BLUE}Tracer disabled: Standard stack traces restored{Colors.ENDC}\n"
            )

    def exception_handler(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """
        Custom exception handler to replace sys.excepthook.

        Args:
            exc_type: The exception type
            exc_value: The exception value/message
            exc_traceback: The traceback object
        """
        if not self.enabled:
            self.original_excepthook(exc_type, exc_value, exc_traceback)
            return

        self._format_exception(exc_type, exc_value, exc_traceback)

    def _format_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """
        Format and print an exception in a more readable way.

        Args:
            exc_type: The exception type
            exc_value: The exception value/message
            exc_traceback: The traceback object
        """
        self._print_header(exc_type, exc_value)
        self._extract_traceback_frames(exc_traceback)
        self._print_stack_trace_frames()
        self._create_data_for_analysis(exc_type, exc_value)

        if self.ai_config.enabled and self.ai_config.api_key:
            self._printer.print(f"{Colors.CYAN}Analyzing error with AI...{Colors.ENDC}\n", 2)
            ai_analysis = self._get_ai_analysis()
        else:
            self._printer.print(
                f"{Colors.WARNING}AI analysis is disabled or API key not provided.{Colors.ENDC}\n"
            )
            return

        self._printer.print(
            f"\n{Colors.BLUE}{Colors.BOLD}Analysis:{Colors.ENDC}\n{ai_analysis.explanation}", 0
        )
        self._printer.print(
            f"\n{Colors.GREEN}{Colors.BOLD}Suggested Fix:{Colors.ENDC}"
            f"\n{ai_analysis.suggested_fix}\n",
            0,
        )

        self._print_footer()

    def _create_data_for_analysis(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
    ) -> None:
        """
        Create a structured representation of the error data for AI analysis.

        Args:
            exc_type: The exception type
            exc_value: The exception value/message

        Returns:
            Dictionary with structured error data
        """
        self._data_for_analysis = DataForAnalysis(
            exception_type=exc_type.__name__,
            exception_message=str(exc_value),
            frames=self._traceback_frames,
            most_relevant_frame=self._get_last_frame(),
        )

    def _get_last_frame(self) -> Frame:
        # Create empty frame if no frames exist
        if not self._traceback_frames:
            return Frame(filename="", lineno=0, function="", lines=[], code_snippet="", locals={})
        return self._traceback_frames[-1]

    def _get_ai_analysis(self) -> AiAnalysis:
        """
        Get AI-powered analysis for the error.

        Returns:
            Dictionary with explanation and suggested fix
        """
        self._ai_analysis_failed = True  # Flag to track AI analysis failure
        _indicator_started = False
        try:
            cache_key = self._create_hash_key()
            exists = self._read_from_cache(cache_key) if self._caching_is_enabled() else None
            if exists:
                return exists

            if self._ai_client is None:
                raise ValueError("AI client is not configured")

            if self._progress_indicator is not None:
                _indicator_started = True
                self._progress_indicator.start()

            with Timer() as timer:
                analysis = self._ai_client.get_analysis(
                    system_prompt=self._system_prompt,
                    user_prompt=self._get_user_prompt(),
                )

            if self._progress_indicator is not None and _indicator_started:
                _indicator_started = False
                self._progress_indicator.stop()

            self._ai_analysis_failed = False

            self._printer.print(
                f"{Colors.CYAN}AI Analysis completed in {timer.elapsed():.2f}s{Colors.ENDC}\n"
            )
            self._write_to_cache(analysis, cache_key)

            return analysis
        except Exception as e:
            if self._progress_indicator is not None and _indicator_started:
                self._progress_indicator.stop()

            if self._ai_analysis_failed:
                return AiAnalysis(
                    explanation=f"AI analysis failed: {str(e)}.",
                    suggested_fix="Unable to provide AI-powered suggestions due to an error.",
                )

            self._printer.print(f"{Colors.FAIL}Error during AI analysis: {str(e)}{Colors.ENDC}\n")
            return analysis

    def _write_to_cache(self, analysis: AiAnalysis, key: str) -> None:
        """
        Cache the AI analysis response.

        Args:
            analysis: The AI analysis response to cache
            key: The cache key to use for storing the response

        Returns:
            None
        """
        if self._caching_is_enabled() and self._cache is not None:
            self._printer.print(
                f"{Colors.CYAN}Caching AI response with key {key}{Colors.ENDC}\n", 2
            )
            self._cache.set(
                key=key,
                value=CacheData(
                    timestamp=time.time(),
                    explanation=analysis.explanation,
                    suggested_fix=analysis.suggested_fix,
                ),
            )
            return

    def _read_from_cache(self, key: str) -> Union[AiAnalysis, None]:
        """
        Read an AI analysis response from the cache.

        Args:
            key: The cache key to look up
        Returns:
            AiAnalysis object if found in cache, None otherwise
        """
        with Timer() as timer:
            data = (
                self._cache.get(key)
                if (self._caching_is_enabled() and self._cache is not None)
                else None
            )
            if data:
                self._printer.print(
                    f"{Colors.CYAN}Using cached AI response with key {key}{Colors.ENDC}\n", 2
                )
                self._printer.print(
                    f"{Colors.CYAN}Cache read completed in {timer.elapsed():.2f}s{Colors.ENDC}\n"
                )
                return AiAnalysis(explanation=data.explanation, suggested_fix=data.suggested_fix)
        return None

    def _print_stack_trace_frames(self) -> None:
        self._printer.print(f"{Colors.BOLD}Stack Trace: (most recent call last){Colors.ENDC}\n", 0)
        for i, frame in enumerate(self._traceback_frames):
            self._print_frame(i + 1, len(self._traceback_frames), frame)

    def _extract_traceback_frames(self, tb: Optional[TracebackType]) -> None:
        """
        Extract useful information from the traceback frames.

        Args:
            tb: The traceback object

        Returns:
            List of dictionaries with frame information
        """
        frames = []
        current = tb

        while current is not None:
            frame = current.tb_frame
            filename = frame.f_code.co_filename
            lineno = current.tb_lineno
            function = frame.f_code.co_name

            # Get context lines (code around the error)
            lines = []
            for i in range(lineno - 3, lineno + 2):
                if i > 0:  # Line numbers start at 1
                    line = linecache.getline(filename, i)
                    if line:
                        lines.append((i, line.rstrip()))

            # Add to frames list
            frames.append(
                Frame.model_validate(
                    {
                        "filename": filename,
                        "lineno": lineno,
                        "function": function,
                        "lines": lines,
                        "code_snippet": "\n".join([f"{ln}: {lc}" for ln, lc in lines]),
                        "locals": {k: self._format_value(v) for k, v in frame.f_locals.items()},
                    }
                )
            )

            current = current.tb_next
        self._traceback_frames = frames  # Store for AI analysis

    def _print_frame(self, index: int, total: int, frame: Frame) -> None:
        """
        Print a single frame from the traceback.

        Args:
            index: The frame number
            total: Total number of frames objects
            frame: A Frame object containing frame information
        """
        full_path = frame.filename

        # Frame header
        self._printer.print(f"Frame{Colors.BLUE}{Colors.BOLD}[{index}/{total}]{Colors.ENDC}, ", 0)
        self._printer.print(f'file {Colors.BOLD}"{full_path}"{Colors.ENDC}, ', 0)
        self._printer.print(f"line {Colors.BOLD}{frame.lineno}{Colors.ENDC}, ", 0)
        self._printer.print(f"in {Colors.CYAN}{Colors.BOLD}{frame.function}{Colors.ENDC}\n", 0)

        # Code context
        for line_no, line_content in frame.lines:
            prefix = "  > " if line_no == frame.lineno else "    "
            color = Colors.FAIL if line_no == frame.lineno else ""
            end_color = Colors.ENDC if line_no == frame.lineno else ""
            self._printer.print(f"{color}{prefix}{line_no}: {line_content}{end_color}\n", 0)

        # Local variables (if enabled and verbosity level is high enough)
        if self.show_locals and frame.locals:
            self._printer.print(f"\n  {Colors.WARNING}Local variables:{Colors.ENDC}\n", 2)
            for name, value in frame.locals.items():
                # Skip private variables and big objects
                if not name.startswith("__") and len(str(value)) < 200:
                    self._printer.print(f"    {Colors.BOLD}{name}{Colors.ENDC} = {value}\n", 2)

        print()  # Add a blank line between frames

    def _create_hash_key(self) -> str:
        # Ensure data_for_analysis exists before using it
        if not self._data_for_analysis:
            return "no_data_available"

        _key_str = f"""
        {self._data_for_analysis.exception_type}:
        {self._data_for_analysis.exception_message}:
        {self._data_for_analysis.most_relevant_frame.function}:
        {os.path.basename(self._data_for_analysis.most_relevant_frame.filename)}:
        {self._data_for_analysis.most_relevant_frame.code_snippet}
        """
        error_hash = hashlib.md5(_key_str.encode()).hexdigest()
        return error_hash

    def _get_user_prompt(self) -> str:
        # Ensure data_for_analysis exists before using it
        if not self._data_for_analysis:
            return "Error: No analysis data available."

        return f"""
        Error analysis request. Please analyze this Python error and provide:
        1. A clear explanation of what's happening
        2. A suggested fix

        Exception Type: {self._data_for_analysis.exception_type}
        Error Message: {self._data_for_analysis.exception_message}

        Most relevant code (error at line {self._data_for_analysis.most_relevant_frame.lineno}):
        {self._data_for_analysis.most_relevant_frame.code_snippet}

        Relevant local variables:
        {json.dumps(self._data_for_analysis.most_relevant_frame.locals, indent=2)}

        Format your response as JSON with 'explanation' and 'suggested_fix' keys.
        """

    def _caching_is_enabled(self) -> bool:
        """
        Check if caching is enabled for AI responses.

        Returns:
            True if caching is enabled, False otherwise
        """
        return self.ai_config.use_cache and self._cache is not None

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Format a value for display, limiting its size.

        Args:
            value: The value to format

        Returns:
            A string representation of the value
        """
        try:
            repr_value = repr(value)
            if len(repr_value) > _MAX_STR_LEN:
                repr_value = repr_value[:97] + "..."
            return repr_value
        except Exception as e:
            return f"<unprintable value of type {type(value).__name__}>: {str(e)}"

    def _print_header(self, exc_type: Type[BaseException], exc_value: BaseException) -> None:
        header = f"{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n"
        header += f"{Colors.FAIL}{Colors.BOLD} {exc_type.__name__}: {exc_value}{Colors.ENDC}\n"
        header += f"{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n"
        self._printer.print(header, 0)

    def _print_footer(self) -> None:
        footer = f"{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n"
        footer += f"{Colors.FAIL}{Colors.BOLD}End of Traceback{Colors.ENDC}\n"
        footer += f"{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n"
        self._printer.print(footer, 0)


# Create a singleton instance with minimal eager initialization
_tracer = Tracer(printer=ConsolePrinter())

# Public API
enable = _tracer.enable
disable = _tracer.disable
analyze = _tracer.analyze
analyzer = _tracer.analyzer
analyze_exception = _tracer.analyze_exception


# Allow custom printers to be injected
def set_printer(printer: PrinterInterface) -> None:
    """Set a custom printer for the tracer."""
    _tracer._printer = printer
