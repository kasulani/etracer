"""
Timer utilities for etracer.
"""

import time
from typing import Any
from .printer import Colors
from ..interfaces import TimerInterface


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

    def __enter__(self) -> "Timer":
        """
        Start the timer when entering the context.

        Returns:
            The timer instance
        """
        self._start_time = time.time()
        self._running = True
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
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
