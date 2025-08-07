"""
Progress indicators for etracer.
"""

import sys
import time
import threading
import itertools
from typing import TextIO, Optional

from .printer import Colors
from ..interfaces import ProgressIndicatorInterface

# Constants
_THREAD_TIME_OUT = 0.5  # seconds for spinner thread to stop gracefully


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

    def __init__(
        self, stop_event: threading.Event, output: TextIO = sys.stdout, message: str = "Processing"
    ):
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
        spinner = itertools.cycle(["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"])
        start_time = time.time()
        while not self._stop_event.is_set():
            elapsed = time.time() - start_time
            self._output.write(
                f"\r{Colors.CYAN}{self._message} {next(spinner)} {elapsed:.1f}s{Colors.ENDC}"
            )
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
