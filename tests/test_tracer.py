import json
import sys
import time
import unittest
from unittest.mock import Mock

import etracer
from etracer import AiAnalysis, CacheData, DataForAnalysis, Frame, Tracer
from etracer.utils import CacheConfig, ConsolePrinter, FileBasedCache

from .mocks import MockAIClient, MockCache, MockPrinter, MockProgressIndicator


class TestTracer(unittest.TestCase):
    def setUp(self):
        """Set up the Tracer instance for testing"""

        self._tracer = Tracer(
            ai_client=MockAIClient(),
            printer=MockPrinter(),
            progress_indicator=MockProgressIndicator(),
            cache=MockCache(),
        )

    def tearDown(self):
        self._tracer.disable()
        self._tracer = None

    def assert_exception_was_caught_and_handled(self):
        # Verify that the exception was caught and handled
        self.assertEqual(self._tracer._data_for_analysis.exception_type, ZeroDivisionError.__name__)
        self.assertEqual(self._tracer._data_for_analysis.exception_message, "division by zero")

    def assert_no_exception_was_caught_and_handled(self):
        # Verify that the exception was not caught and handled
        self.assertListEqual(self._tracer._traceback_frames, [])
        self.assertIsNone(self._tracer._data_for_analysis)
        self.assertEqual(
            self._tracer._get_last_frame(),
            Frame(filename="", lineno=0, function="", lines=[], code_snippet="", locals={}),
        )
        self.assertEqual(self._tracer._create_hash_key(), "no_data_available")
        self.assertEqual(self._tracer._get_user_prompt(), "Error: No analysis data available.")

    def _enable_tracer(self):
        self._tracer.enable(
            verbosity=0,
            enable_ai=True,
            api_key="test_key",
            model="test_model",
            base_url="https://test.com",
        )

    def test_format_exception_happy_path(self):
        """Test the format_exception method of Tracer happy path"""
        cache = MockCache()
        ai_client = MockAIClient()
        progress_indicator = MockProgressIndicator()

        cache._mock_get_method.return_value = None  # Make cache miss to force using AI
        cache._mock_set_method.side_effect = None  # Cache write works normally
        progress_indicator._mock_start_method.return_value = None
        progress_indicator._mock_stop_method.return_value = None

        # Inject our mocks into the tracer
        self._tracer._cache = cache
        self._tracer._ai_client = ai_client
        self._tracer._progress_indicator = progress_indicator

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        # Create a simple error to analyze
        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Call the method under test
            self._tracer._format_exception(exc_type, exc_value, exc_traceback)

            # Do assertions
            self.assertFalse(self._tracer._ai_analysis_failed)
            self.assertIsInstance(self._tracer._traceback_frames, list)
            self.assertEqual(len(self._tracer._traceback_frames), 1)
            self.assertIsInstance(self._tracer._data_for_analysis, DataForAnalysis)
            self.assert_exception_was_caught_and_handled()

            # Verify methods in the flow were called
            progress_indicator._mock_start_method.assert_called_once()
            progress_indicator._mock_stop_method.assert_called_once()
            cache._mock_get_method.assert_called_once()
            cache._mock_set_method.assert_called_once()
            ai_client._mock_get_analysis_method.assert_called_once()

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

    def test_get_ai_analysis_happy_path(self):
        """Test the _get_ai_analysis method of Tracer happy path"""
        cache = MockCache()
        ai_client = MockAIClient()
        progress_indicator = MockProgressIndicator()

        cache._mock_get_method.return_value = None  # Make cache miss to force using AI
        cache._mock_set_method.side_effect = None  # Cache write works normally

        expected_explanation = (
            "A ZeroDivisionError is raised when your code attempts to divide a number."
        )
        expected_fix = (
            "Before performing the division (or modulo), validate that the denominator is not zero."
        )
        ai_client._mock_get_analysis_method.return_value = AiAnalysis(
            explanation=expected_explanation, suggested_fix=expected_fix
        )

        # Inject our mocks into the tracer
        self._tracer._cache = cache
        self._tracer._progress_indicator = progress_indicator
        self._tracer._ai_client = ai_client

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        # Create a ZeroDivisionError to analyze
        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Set up the test conditions
            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            # Call the method under test
            analysis = self._tracer._get_ai_analysis()

            # Verify results
            self.assertFalse(self._tracer._ai_analysis_failed)
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIsInstance(analysis.explanation, str)
            self.assertIsInstance(analysis.suggested_fix, str)

            # The explanation should match what's returned by MockAIClient
            self.assertIn(expected_explanation, analysis.explanation)
            self.assertIn(expected_fix, analysis.suggested_fix)

            # Verify that the expected methods were called
            ai_client._mock_get_analysis_method.assert_called_once()
            cache._mock_get_method.assert_called_once()
            cache._mock_set_method.assert_called_once()
            progress_indicator._mock_start_method.assert_called_once()
            progress_indicator._mock_stop_method.assert_called_once()

    def test_get_ai_analysis_when_ai_client_is_none(self):
        """Test _get_ai_analysis when cache read from fails but is caught by _get_ai_analysis try/except"""
        cache = MockCache()
        progress_indicator = MockProgressIndicator()

        # Set up test conditions
        cache._mock_set_method.return_value = None  # Cache miss
        progress_indicator._mock_start_method.return_value = None
        progress_indicator._mock_stop_method.return_value = None

        self._tracer._cache = cache
        self._tracer._progress_indicator = progress_indicator
        self._tracer._ai_client = None

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Set up test conditions
            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            # Call the method under test
            analysis = self._tracer._get_ai_analysis()

            # Do assertions
            self.assertTrue(self._tracer._ai_analysis_failed)
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIn("AI analysis failed", analysis.explanation)
            self.assertIn("AI analysis failed: AI client is not configured", analysis.explanation)
            self.assertIn("Unable to provide AI-powered suggestions", analysis.suggested_fix)

            # Verify that cache.set was called and raised the exception
            cache._mock_get_method.assert_called_once()
            cache._mock_set_method.assert_not_called()
            progress_indicator._mock_start_method.assert_not_called()
            progress_indicator._mock_stop_method.assert_not_called()

    def test_get_ai_analysis_when_cache_write_fails(self):
        """Test _get_ai_analysis when cache write fails"""
        cache = MockCache()
        progress_indicator = MockProgressIndicator()

        expected_explanation = (
            "A ZeroDivisionError is raised when your code attempts to divide a number."
        )
        expected_fix = (
            "Before performing the division (or modulo), validate that the denominator is not zero."
        )

        # Set up test conditions
        cache._mock_get_method.return_value = None
        cache._mock_set_method.side_effect = Exception("Cache write failed")
        progress_indicator._mock_start_method.return_value = None
        progress_indicator._mock_stop_method.return_value = None

        self._tracer._cache = cache
        self._tracer._progress_indicator = progress_indicator

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Set up test conditions
            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            # Call the method under test
            analysis = self._tracer._get_ai_analysis()

            # Do assertions
            self.assertFalse(self._tracer._ai_analysis_failed)
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIn(expected_explanation, analysis.explanation)
            self.assertIn(expected_fix, analysis.suggested_fix)

            # Verify that cache.get was called and cache.set raised the exception
            cache._mock_get_method.assert_called_once()
            cache._mock_set_method.assert_called_once()
            progress_indicator._mock_start_method.assert_called_once()
            progress_indicator._mock_stop_method.assert_called_once()

    def test_get_ai_analysis_when_ai_analysis_fails(self):
        """Test _get_ai_analysis when AI analysis fails"""
        cache = MockCache()
        ai_client = MockAIClient()
        progress_indicator = MockProgressIndicator()

        # Set up test conditions
        cache._mock_get_method.return_value = None
        cache._mock_set_method.side_effect = None  # Cache write works normally
        progress_indicator._mock_start_method.return_value = None
        progress_indicator._mock_stop_method.return_value = None

        # Simulate AI client failure
        ai_client._mock_get_analysis_method.side_effect = Exception(
            "Test exception: Failed to get AI analysis"
        )

        # Inject our mocks into the tracer
        self._tracer._cache = cache
        self._tracer._ai_client = ai_client
        self._tracer._progress_indicator = progress_indicator

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        try:
            x = 1
            _ = x / 0
        except ZeroDivisionError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Set up the test conditions
            self._tracer._extract_traceback_frames(exc_traceback)
            self._tracer._create_data_for_analysis(exc_type, exc_value)

            # Call the method under test
            analysis = self._tracer._get_ai_analysis()

            # Do assertions
            self.assertTrue(self._tracer._ai_analysis_failed)
            self.assertIsInstance(analysis, AiAnalysis)
            self.assertIn("AI analysis failed", analysis.explanation)
            self.assertIn("Test exception: Failed to get AI analysis", analysis.explanation)
            self.assertIn("Unable to provide AI-powered suggestions", analysis.suggested_fix)
            self.assert_exception_was_caught_and_handled()

            # Verify that cache.get was called and cache.set was not called
            cache._mock_get_method.assert_called_once()
            cache._mock_set_method.assert_not_called()
            ai_client._mock_get_analysis_method.assert_called_once()
            progress_indicator._mock_start_method.assert_called_once()
            progress_indicator._mock_stop_method.assert_called_once()

    def test_get_ai_analysis_from_cache(self):
        """Test the _get_ai_analysis_from_cache method of Tracer"""
        cache = MockCache()
        cache._mock_get_method.return_value = CacheData(
            timestamp=time.time(),
            explanation="Mock cached explanation: ZeroDivisionError",
            suggested_fix="Mock cached suggested fix: division by zero",
        )
        self._tracer._cache = cache

        try:
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

    def test_analyzer_context_manager(self):
        """Test the analyzer context manager functionality with a real exception"""

        self._tracer.enabled = False  # Ensure tracer is disabled initially
        original_excepthook = self._tracer.original_excepthook

        mock_original_excepthook = Mock()
        self._tracer.original_excepthook = mock_original_excepthook

        with self._tracer.analyzer():
            _ = 1 / 0  # This should raise ZeroDivisionError

        # Verify
        self.assert_no_exception_was_caught_and_handled()
        mock_original_excepthook.assert_called_once()
        args = mock_original_excepthook.call_args[0]
        self.assertEqual(args[0], ZeroDivisionError)  # exc_type
        self.assertIsInstance(args[1], ZeroDivisionError)  # exc_value
        self.assertEqual(str(args[1]), "division by zero")  # exc_message
        self.assertIsNotNone(args[2])  # exc_traceback

        # Restore the original excepthook
        self._tracer.original_excepthook = original_excepthook

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        with self._tracer.analyzer():
            _ = 1 + 1  # This should not raise an exception

        self.assert_no_exception_was_caught_and_handled()

        with self._tracer.analyzer():
            _ = 1 / 0  # This should raise ZeroDivisionError

        self.assert_exception_was_caught_and_handled()

    def test_analyze_decorator(self):
        """Test the analyze decorator functionality"""

        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        @self._tracer.analyze
        def function_that_raises_no_exception() -> int:
            return 1 + 1

        function_that_raises_no_exception()
        self.assert_no_exception_was_caught_and_handled()

        @self._tracer.analyze
        def function_that_raises_exception():
            return 1 / 0

        # The function should not raise an exception because the decorator catches it
        try:
            function_that_raises_exception()
        except ZeroDivisionError:
            self.fail("Analyze decorator didn't catch the exception")

        self.assert_exception_was_caught_and_handled()

    def test_analyze_exception(self):
        """Test the analyze_exception method"""

        self._tracer.enabled = False
        original_excepthook = self._tracer.original_excepthook

        # Create a mock for the original excepthook
        mock_original_excepthook = Mock()
        self._tracer.original_excepthook = mock_original_excepthook

        try:
            _ = 1 / 0
        except Exception as e:
            self._tracer.analyze_exception(e)

            # Verify that original_excepthook was called with the right arguments
            self.assert_no_exception_was_caught_and_handled()
            mock_original_excepthook.assert_called_once()
            args = mock_original_excepthook.call_args[0]
            self.assertEqual(args[0], ZeroDivisionError)  # exc_type
            self.assertIsInstance(args[1], ZeroDivisionError)  # exc_value
            self.assertEqual(str(args[1]), "division by zero")  # exc_message
            self.assertIsNotNone(args[2])  # exc_traceback

        # Restore the original excepthook
        self._tracer.original_excepthook = original_excepthook

        # Now test when tracer is enabled
        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        try:
            _ = 1 / 0
        except Exception as e:
            # This should not raise any exceptions
            self._tracer.analyze_exception(e)

        self.assert_exception_was_caught_and_handled()

    def test_printer_functionality(self):
        """Test the printer functionality"""

        etracer.set_printer(MockPrinter())

        # Test the ConsolePrinter directly
        printer = ConsolePrinter(verbosity=2)
        self.assertEqual(printer.verbosity, 2)

        # Test verbosity setting
        printer.set_verbosity(1)
        self.assertEqual(printer.verbosity, 1)

        # For print, we need to patch sys.stdout to capture the output
        # We'll just test that it doesn't raise exceptions
        printer.print("Test message", 0)
        printer.print("Higher verbosity message", 2)  # Should not be printed with verbosity 1

    def test_cache_operations(self):
        """Test cache operations directly"""

        # Create a test cache instance
        cache_config = CacheConfig()
        cache = FileBasedCache(cache_config)

        # Create test data
        test_data = CacheData(
            timestamp=time.time(), explanation="Test explanation", suggested_fix="Test fix"
        )

        # Set a value
        cache.set("test_key", test_data)

        # Get the value back
        retrieved_data = cache.get("test_key")
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data.explanation, "Test explanation")
        self.assertEqual(retrieved_data.suggested_fix, "Test fix")

        # Test with non-existent key
        not_found = cache.get("non_existent_key")
        self.assertIsNone(not_found)

    def test_formatter_functionality(self):
        """Test the formatting functionality"""
        self._enable_tracer()
        self.assertTrue(self._tracer.enabled)
        self.assertTrue(self._tracer.ai_config.enabled)

        # Test format_value method
        result = self._tracer._format_value(12345)
        self.assertEqual(result, "12345")

        # Test with a string that would be truncated
        long_string = "x" * 200
        result = self._tracer._format_value(long_string)
        self.assertEqual(len(result), 100)  # Should be truncated to _MAX_STR_LEN
        self.assertTrue(result.endswith("..."))

        # Test with a complex object
        class TestObj:
            def __repr__(self):
                return "<TestObj>"

        obj = TestObj()
        result = self._tracer._format_value(obj)
        self.assertEqual(result, "<TestObj>")

        # Test the exception handling branch (lines 545-546)
        class BrokenReprObj:
            def __repr__(self):
                raise ValueError("This object cannot be represented")

        broken_obj = BrokenReprObj()
        result = self._tracer._format_value(broken_obj)
        self.assertTrue(result.startswith("<unprintable value of type BrokenReprObj>"))
        self.assertIn("This object cannot be represented", result)

    def test_all_verbosity_levels(self):
        """Test exception handling with different verbosity levels"""
        for verbosity in [0, 1, 2]:
            tracer = Tracer(
                ai_client=MockAIClient(),
                printer=MockPrinter(),
                progress_indicator=MockProgressIndicator(),
                cache=MockCache(),
            )
            tracer.enable(verbosity=verbosity)

            # Verify verbosity setting
            self.assertEqual(tracer.verbosity, verbosity)
            # Verify show_locals setting based on verbosity
            self.assertEqual(tracer.show_locals, verbosity == 2)

            # Test that exception handling works with different verbosity levels
            try:
                _ = 1 / 0
            except Exception as e:
                tracer.analyze_exception(e)  # Should not raise any exceptions

    def test_ai_config(self):
        """Test AI configuration settings"""

        self._tracer.disable()  # Ensure tracer is disabled initially
        self.assertFalse(self._tracer.ai_config.enabled)

        # Test enabling AI
        self._enable_tracer()

        # Verify settings were applied
        self.assertTrue(self._tracer.ai_config.enabled)
        self.assertEqual(self._tracer.ai_config.api_key, "test_key")
        self.assertEqual(self._tracer.ai_config.model, "test_model")
        self.assertEqual(self._tracer.ai_config.base_url, "https://test.com")


if __name__ == "__main__":
    unittest.main()
