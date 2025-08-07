import time
import unittest
import sys
import json
from typing import Union
from etracer import (
    Tracer,
    Frame,
    DataForAnalysis,
    AiAnalysis,
    CacheData,
    AnalysisGetterInterface,
    CacheInterface,
)
from etracer.utils import NoOpPrinter, NoOpProgressIndicator


# Mock classes for testing
class MockAIClient(AnalysisGetterInterface):
    def __init__(self):
        pass

    def get_analysis(self, system_prompt: str, user_prompt: str) -> AiAnalysis:
        return AiAnalysis(
            explanation="A ZeroDivisionError is raised when your code attempts to divide a number.",
            suggested_fix="Before performing the division (or modulo), validate that the denominator is not zero.",
        )


class MockCache(CacheInterface):
    def __init__(self, cache_data: dict = None, use_default: bool = False):
        self._cache: dict = {"default": cache_data} if cache_data is not None else {}
        self._use_default = use_default

    def get(self, key: str) -> Union[CacheData, None]:
        if key not in self._cache and self._use_default:
            return CacheData.model_validate(self._cache.get("default"))
        return CacheData.model_validate(self._cache.get(key)) if key in self._cache else None

    def set(self, key: str, value: CacheData) -> None:
        self._cache[key] = value.model_dump()

    def item_count(self) -> int:
        return len(self._cache)


class TestTracer(unittest.TestCase):
    def setUp(self):
        self._tracer = Tracer(
            ai_client=MockAIClient(),
            printer=NoOpPrinter(),
            progress_indicator=NoOpProgressIndicator(),
            cache=MockCache(),
        )
        self._tracer.enable(verbosity=0)  # Set verbosity to 0 for minimal output during tests

    def tearDown(self):
        self._tracer.disable()
        self._tracer = None

    def test_extract_traceback_frames(self):
        """Test the _extract_traceback_frames method of Tracer"""

        # Create a controlled exception to get a traceback object
        try:
            # Create a simple error to analyze
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            self._tracer._extract_traceback_frames(exc_traceback)
            self.assertIsInstance(self._tracer._traceback_frames, list)

            frames = self._tracer._traceback_frames
            self.assertEqual(len(frames), 1)

            for frame in frames:
                self.assertIsInstance(frame, Frame)
                self.assertIsInstance(frame.function, str)
                self.assertEqual(frame.function, "test_extract_traceback_frames")
                self.assertIsInstance(frame.filename, str)
                self.assertIsInstance(frame.lineno, int)
                self.assertIsInstance(frame.lines, list)
                self.assertIsInstance(frame.locals, dict)
                self.assertIn("x", frame.locals)
                self.assertEqual(eval(frame.locals["x"]), 1)

    def test_create_data_for_analysis(self):
        """Test the _create_data_for_analysis method of Tracer"""

        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            self._tracer._extract_traceback_frames(exc_traceback)  # Extract frames first
            self._tracer._create_data_for_analysis(exc_type, exc_value)  # Create data for analysis
            data = self._tracer._data_for_analysis

            self.assertIsInstance(data, DataForAnalysis)
            self.assertIsInstance(data.exception_type, str)
            self.assertIsInstance(data.exception_message, str)
            self.assertIsInstance(data.frames, list)
            self.assertEqual(len(data.frames), 1)
            self.assertEqual(data.exception_type, "ZeroDivisionError")
            self.assertEqual(data.exception_message, "division by zero")
            self.assertEqual(data.most_relevant_frame.function, "test_create_data_for_analysis")
            self.assertIn("x", data.most_relevant_frame.locals)
            self.assertEqual(data.most_relevant_frame.locals["x"], "1")

    def test_get_user_prompt(self):
        """Test the _get_user_prompt method of Tracer"""

        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            prompt = self._tracer._get_user_prompt()

            self.assertIsInstance(prompt, str)
            self.assertEqual(
                prompt,
                f"""
        Error analysis request. Please analyze this Python error and provide:
        1. A clear explanation of what's happening
        2. A suggested fix

        Exception Type: {self._tracer._data_for_analysis.exception_type}
        Error Message: {self._tracer._data_for_analysis.exception_message}

        Most relevant code (error at line {self._tracer._data_for_analysis.most_relevant_frame.lineno}):
        {self._tracer._data_for_analysis.most_relevant_frame.code_snippet}

        Relevant local variables:
        {json.dumps(self._tracer._data_for_analysis.most_relevant_frame.locals, indent=2)}

        Format your response as JSON with 'explanation' and 'suggested_fix' keys.
        """,
            )

    def test_get_ai_analysis(self):
        cache = MockCache()
        self._tracer._cache = cache
        try:
            # Create a simple error to analyze
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            self.assertEqual(cache.item_count(), 0)

            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            analysis = self._tracer._get_ai_analysis()
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIsInstance(analysis.explanation, str)
            self.assertIsInstance(analysis.suggested_fix, str)
            self.assertIn(
                "A ZeroDivisionError is raised when your code attempts to divide a number.",
                analysis.explanation,
            )
            self.assertIn(
                "Before performing the division (or modulo), validate that the denominator is not zero.",
                analysis.suggested_fix,
            )

            self.assertEqual(cache.item_count(), 1)

    def test_get_ai_analysis_from_cache(self):
        """Test the _get_ai_analysis_from_cache method of Tracer"""
        self._tracer._cache = MockCache(
            cache_data=CacheData(
                timestamp=time.time(),
                explanation="Mock cached explanation: ZeroDivisionError",
                suggested_fix="Mock cached suggested fix: division by zero",
            ).model_dump(),
            use_default=True,
        )

        try:
            # Create a simple error to analyze
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            analysis = self._tracer._get_ai_analysis()
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIsInstance(analysis.explanation, str)
            self.assertIsInstance(analysis.suggested_fix, str)
            self.assertIn("Mock cached explanation: ZeroDivisionError", analysis.explanation)
            self.assertIn("Mock cached suggested fix: division by zero", analysis.suggested_fix)


if __name__ == "__main__":
    unittest.main()
