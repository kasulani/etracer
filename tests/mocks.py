from typing import Union
from etracer import (
    AiAnalysis,
    CacheData,
    AnalysisGetterInterface,
    CacheInterface,
    PrinterInterface,
    ProgressIndicatorInterface,
)
from unittest.mock import Mock


class MockAIClient(Mock, AnalysisGetterInterface):
    def get_analysis(self, system_prompt: str, user_prompt: str) -> AiAnalysis:
        # Return a mock that can be configured in tests
        return self._mock_get_analysis_method(system_prompt, user_prompt)

    def __init__(self):
        super().__init__()
        self._mock_get_analysis_method = Mock()
        self._mock_get_analysis_method.return_value = AiAnalysis(
            explanation="A ZeroDivisionError is raised when your code attempts to divide a number.",
            suggested_fix="Before performing the division (or modulo), validate that the denominator is not zero.",
        )


class MockCache(Mock, CacheInterface):
    def get(self, key: str) -> Union[CacheData, None]:
        # Return a mock that can be configured in tests
        return self._mock_get_method(key)

    def set(self, key: str, value: CacheData) -> None:
        # Call the mock method
        self._mock_set_method(key, value)

    def __init__(self):
        super().__init__()
        self._mock_get_method = Mock()
        self._mock_set_method = Mock()

        # Set default return value to None - can be overridden in tests
        self._mock_get_method.return_value = None


class MockPrinter(Mock, PrinterInterface):
    def print(self, message: str, verbosity: int = 1) -> None:
        # Call the mock method
        self._mock_print_method(message, verbosity)

    def set_verbosity(self, verbosity: int) -> None:
        # Call the mock method
        self._mock_set_verbosity_method(verbosity)

    def __init__(self):
        super().__init__()
        self._mock_print_method = Mock()
        self._mock_set_verbosity_method = Mock()

        self._mock_print_method.return_value = None  # Default behavior does nothing
        self._mock_set_verbosity_method.return_value = None  # Default behavior does nothing


class MockProgressIndicator(Mock, ProgressIndicatorInterface):
    def start(self) -> None:
        # Call the mock method
        self._mock_start_method()

    def stop(self) -> None:
        # Call the mock method
        self._mock_stop_method()

    def __init__(self):
        super().__init__()
        self._mock_start_method = Mock()
        self._mock_stop_method = Mock()
