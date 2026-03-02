import os
import json
from anthropic import Anthropic
from .prompt_templates import EXTRACTION_PROMPT
from .validator import ExtractionValidator
from .parser import ExtractionParser
from .mock_responses import get_mock_extraction


class ExtractionError(Exception):
    """Raised when extraction fails."""
    pass


class ClaudeExtractionClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = model or os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.max_tokens = int(os.environ.get('CLAUDE_MAX_TOKENS', '4096'))
        self.use_mock = os.environ.get('USE_MOCK_EXTRACTION', 'false').lower() == 'true'
        self.validator = ExtractionValidator()
        self.parser = ExtractionParser()
        if not self.use_mock:
            self.client = Anthropic(api_key=self.api_key)

    def extract(self, flattened_thread: str) -> dict:
        """Extract commercial terms from a flattened email thread."""
        if self.use_mock:
            extraction = get_mock_extraction(flattened_thread)
            extraction = self.validator.adjust_confidence(extraction)
            return extraction

        prompt = EXTRACTION_PROMPT.replace('{flattened_thread}', flattened_thread)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.content[0].text
        except Exception as e:
            raise ExtractionError(f"Claude API call failed: {str(e)}")

        # Parse JSON from response (handles markdown fences)
        try:
            extraction = self.parser.parse_response(raw_text)
        except Exception as e:
            raise ExtractionError(f"Failed to parse Claude response: {str(e)}")

        # Validate and adjust confidence
        is_valid, issues = self.validator.validate(extraction)
        if not is_valid:
            raise ExtractionError(f"Extraction validation failed: {', '.join(issues)}")

        # Apply confidence adjustments
        extraction = self.validator.adjust_confidence(extraction)

        return extraction
