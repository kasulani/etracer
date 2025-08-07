"""
AI client implementation for etracer.
"""

import json
from typing import Optional

# Import OpenAI client
from openai import OpenAI
from ..models import AiAnalysis
from ..interfaces import AnalysisGetterInterface

# API configuration
_DEFAULT_BASE_URL = "https://api.openai.com/v1"
_DEFAULT_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
_DEFAULT_MODEL = "gpt-3.5-turbo"
_DEFAULT_TIMEOUT = 30  # seconds
_TEMPERATURE = 0.3  # Controls randomness in AI responses


class AIConfig:
    """Configuration for AI integration."""

    def __init__(self) -> None:
        self.api_key: Optional[str] = None  # OpenAI API key
        self.api_endpoint: str = _DEFAULT_API_ENDPOINT  # Default API endpoint for AI requests
        self.model: str = _DEFAULT_MODEL  # Default AI model to use
        self.timeout: int = _DEFAULT_TIMEOUT  # Timeout for AI requests in seconds
        self.enabled: bool = False  # Whether AI integration is enabled
        self.use_cache: bool = True  # Whether to use caching for AI responses
        self.base_url: Optional[str] = _DEFAULT_BASE_URL  # Base URL for the AI API

    def configure(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        enabled: Optional[bool] = None,
        use_cache: Optional[bool] = None,
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
                suggested_fix="Enable AI integration to get analysis.",
            )

        self._schema["additionalProperties"] = False

        response = self._ai_client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
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

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("AI response content is None")
        return AiAnalysis.model_validate(json.loads(content))
