"""
Printer implementations for etracer.
"""

from ..interfaces import PrinterInterface


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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

    def set_verbosity(self, verbosity: int) -> None:
        """
        Set the verbosity level.

        Args:
            verbosity: The new verbosity level
        """
        self.verbosity = verbosity


class NoOpPrinter(PrinterInterface):
    """
    Printer implementation that discards all messages (useful for testing).
    """

    def __init__(self) -> None:
        pass

    def print(self, message: str, verbosity: int = 1) -> None:
        pass
