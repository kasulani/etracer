"""
Interface definitions for etracer.

This module contains all protocol classes that define interfaces for the package.
These interfaces provide contracts that implementations must follow.
"""

from typing import Protocol, Union

from .models import AiAnalysis, CacheData


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


class AnalysisGetterInterface(Protocol):
    """Interface for getting AI-powered analysis."""

    def get_analysis(self, system_prompt: str, user_prompt: str) -> AiAnalysis:
        """
        Get AI-powered analysis for the provided error data.

        Args:
            system_prompt: System prompt for AI context
            user_prompt: User prompt for AI analysis

        Returns:
            AiAnalysis object with explanation and suggested fix
        """
        pass


class ProgressIndicatorInterface(Protocol):
    """Interface for progress indicators."""

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
