import os
import logging
from typing import Dict, Any
from anthropic import Anthropic, APIError
from agent.spec_loader import load_all_specs

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Wrapper for Claude API calls.
    Loads system specifications and builds prompts for:
    - Drafting text
    - Revising selected text
    - Outlining / planning
    """

    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("Missing ANTHROPIC_API_KEY environment variable")
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=api_key)
        self.specs: Dict[str, str] = load_all_specs()
        logger.info("Claude client initialized")

        # Build the core system prompt
        self.system_prompt: str = (
            self.specs["system_prompt"]
            + "\n\n"
            + self.specs["master_spec"]
        )

    # ------------------------------------------------
    # Core API Caller
    # ------------------------------------------------
    def _call_claude(self, user_prompt: str, max_tokens: int = 2000) -> str:
        """
        Sends a text query to Claude with the correct system prompt.
        """
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Claude returns a list of message content blocks
            if response.content:
                return response.content[0].text

            return "[No response from Claude]"

        except APIError as e:
            logger.error(f"Claude API error: {e}")
            return f"[Claude API error: {str(e)}]"
        except Exception as e:
            logger.error(f"Unexpected error in Claude client: {e}")
            return f"[Unexpected error: {str(e)}]"

    # ------------------------------------------------
    # PUBLIC FUNCTIONS
    # ------------------------------------------------
    def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Generates new prose using Claude.
        """
        final_prompt = (
            "Write in the hybrid modern-literary style defined in the system specs.\n\n"
            f"{prompt}"
        )
        return self._call_claude(final_prompt, max_tokens)

    def revise_text(self, original_text: str, instructions: str) -> str:
        """
        Sends text to Claude with revision instructions.
        """
        final_prompt = (
            "Revise the following text using the system's literary-modern voice.\n"
            "Preserve meaning unless explicitly told otherwise.\n\n"
            f"INSTRUCTIONS:\n{instructions}\n\n"
            f"ORIGINAL TEXT:\n{original_text}"
        )
        return self._call_claude(final_prompt)

    def outline_chapter(self, summary: str) -> str:
        """
        Generates a chapter outline from a short summary.
        """
        prompt = (
            "Create a detailed chapter outline based on this description:\n\n"
            f"{summary}"
        )
        return self._call_claude(prompt)
