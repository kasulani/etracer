"""Tests for the AIClient class."""

import unittest
from unittest.mock import patch, Mock

from etracer.utils import AIClient, AIConfig
from etracer import AiAnalysis


class TestAIConfig(unittest.TestCase):
    """Test the AIConfig class."""

    def test_init(self):
        """Test the __init__ method."""
        config = AIConfig()
        self.assertIsNone(config.api_key)
        self.assertEqual(config.model, "gpt-3.5-turbo")
        self.assertEqual(config.timeout, 30)
        self.assertFalse(config.enabled)
        self.assertTrue(config.use_cache)
        self.assertEqual(config.base_url, "https://api.openai.com/v1")

    def test_configure(self):
        """Test the configure method."""
        config = AIConfig()

        # Test setting all values
        config.configure(
            api_key="test_key",
            base_url="https://test.url",
            model="test_model",
            timeout=60,
            enabled=True,
            use_cache=False,
        )
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.base_url, "https://test.url")
        self.assertEqual(config.model, "test_model")
        self.assertEqual(config.timeout, 60)
        self.assertTrue(config.enabled)
        self.assertFalse(config.use_cache)

        # Test setting only some values
        config = AIConfig()
        config.configure(api_key="test_key", enabled=True)
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.base_url, "https://api.openai.com/v1")  # Default unchanged
        self.assertEqual(config.model, "gpt-3.5-turbo")  # Default unchanged
        self.assertEqual(config.timeout, 30)  # Default unchanged
        self.assertTrue(config.enabled)
        self.assertTrue(config.use_cache)  # Default unchanged


class TestAIClient(unittest.TestCase):
    """Test the AIClient class."""

    def setUp(self):
        """Set up the test."""
        self.config = AIConfig()
        self.config.configure(
            api_key="test_key",
            base_url="https://test.url",
            model="test_model",
            timeout=60,
            enabled=True,
        )

        # Mock the OpenAI client
        self.mock_openai_patcher = patch("etracer.utils.ai_client.OpenAI")
        self.mock_openai = self.mock_openai_patcher.start()

        # Create a client instance with mocked OpenAI
        self.client = AIClient(self.config)

    def tearDown(self):
        """Clean up after the test."""
        self.mock_openai_patcher.stop()

    def test_init(self):
        """Test the __init__ method."""
        # Verify the AI client was initialized with the correct parameters
        self.mock_openai.assert_called_once_with(base_url="https://test.url", api_key="test_key")
        self.assertEqual(self.client.config, self.config)

    def test_get_analysis_without_api_key(self):
        """Test get_analysis with no API key."""
        # Setup client with no API key
        config = AIConfig()
        config.enabled = True
        config.api_key = None
        client = AIClient(config)

        # Test that it raises a ValueError
        with self.assertRaises(ValueError) as context:
            client.get_analysis("system prompt", "user prompt")

        self.assertEqual(str(context.exception), "API key is not set.")

    def test_get_analysis_disabled(self):
        """Test get_analysis when AI is disabled."""
        # Setup client with disabled AI
        config = AIConfig()
        config.api_key = "test_key"
        config.enabled = False
        client = AIClient(config)

        # Test that it returns a disabled message
        result = client.get_analysis("system prompt", "user prompt")
        self.assertIsInstance(result, AiAnalysis)
        self.assertEqual(result.explanation, "AI integration is disabled.")
        self.assertEqual(result.suggested_fix, "Enable AI integration to get analysis.")

    @patch("etracer.utils.ai_client.json")
    def test_get_analysis_successful(self, mock_json):
        """Test successful get_analysis call."""
        # Set up the mock response from OpenAI
        mock_completion = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = '{"explanation": "test explanation", "suggested_fix": "test fix"}'
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]

        self.mock_openai.return_value.chat.completions.create.return_value = mock_completion
        mock_json.loads.return_value = {
            "explanation": "test explanation",
            "suggested_fix": "test fix",
        }

        # Call the method
        result = self.client.get_analysis("system prompt", "user prompt")

        # Verify the result
        self.assertIsInstance(result, AiAnalysis)
        self.assertEqual(result.explanation, "test explanation")
        self.assertEqual(result.suggested_fix, "test fix")

        # Verify the OpenAI API was called correctly
        self.mock_openai.return_value.chat.completions.create.assert_called_once()
        call_args = self.mock_openai.return_value.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "test_model")
        self.assertEqual(call_args["messages"][0]["role"], "system")
        self.assertEqual(call_args["messages"][0]["content"], "system prompt")
        self.assertEqual(call_args["messages"][1]["role"], "user")
        self.assertEqual(call_args["messages"][1]["content"], "user prompt")
        self.assertEqual(call_args["temperature"], 0.3)
        self.assertEqual(call_args["timeout"], 60)

    def test_get_analysis_none_content(self):
        """Test get_analysis with None content response."""
        # Set up the mock response from OpenAI with None content
        mock_completion = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]

        self.mock_openai.return_value.chat.completions.create.return_value = mock_completion

        # Test that it raises a ValueError
        with self.assertRaises(ValueError) as context:
            self.client.get_analysis("system prompt", "user prompt")

        self.assertEqual(str(context.exception), "AI response content is None")


if __name__ == "__main__":
    unittest.main()
