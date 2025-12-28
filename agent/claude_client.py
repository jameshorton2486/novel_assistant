import os
from anthropic import Anthropic, APIError
from agent.spec_loader import load_all_specs


class ClaudeClient:
    """
    Wrapper for Claude 3.7 Sonnet calls.
    Loads system specifications and builds prompts for:
    - Drafting text
    - Revising selected text
    - Outlining / planning
    """

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=api_key)
        self.specs = load_all_specs()

        # Build the core system prompt
        self.system_prompt = (
            self.specs["system_prompt"]
            + "\n\n"
            + self.specs["master_spec"]
        )

    # ------------------------------------------------
    # Core API Caller
    # ------------------------------------------------
    def _call_claude(self, user_prompt: str) -> str:
        """
        Sends a text query to Claude 3.7 Sonnet with the correct system prompt.
        """
        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
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
            return f"[Claude API error: {str(e)}]"
        except Exception as e:
            return f"[Unexpected error: {str(e)}]"

    # ------------------------------------------------
    # PUBLIC FUNCTIONS
    # ------------------------------------------------
    def generate_text(self, prompt: str) -> str:
        """
        Generates new prose using Claude.
        """
        final_prompt = (
            "Write in the hybrid modern-literary style defined in the system specs.\n\n"
            f"{prompt}"
        )
        return self._call_claude(final_prompt)

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
