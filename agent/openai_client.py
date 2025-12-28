import os
from openai import OpenAI, APIError
from agent.spec_loader import load_all_specs

class OpenAIClient:
    """
    Wrapper for OpenAI GPT-4o calls.
    Loads system specifications and builds prompts for:
    - Drafting text
    - Revising selected text
    - Outlining / planning
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=api_key)
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
    def _call_openai(self, user_prompt: str) -> str:
        """
        Sends a text query to GPT-4o with the correct system prompt.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000
            )

            if response.choices:
                return response.choices[0].message.content

            return "[No response from OpenAI]"

        except Exception as e:
            return f"[OpenAI API error: {str(e)}]"

    # ------------------------------------------------
    # PUBLIC FUNCTIONS
    # ------------------------------------------------
    def generate_text(self, prompt: str) -> str:
        """
        Generates new prose using GPT-4o.
        """
        final_prompt = (
            "Write in the hybrid modern-literary style defined in the system specs.\n\n"
            f"{prompt}"
        )
        return self._call_openai(final_prompt)

    def revise_text(self, original_text: str, instructions: str) -> str:
        """
        Sends text to GPT-4o with revision instructions.
        """
        final_prompt = (
            "Revise the following text using the system's literary-modern voice.\n"
            "Preserve meaning unless explicitly told otherwise.\n\n"
            f"INSTRUCTIONS:\n{instructions}\n\n"
            f"ORIGINAL TEXT:\n{original_text}"
        )
        return self._call_openai(final_prompt)

    def outline_chapter(self, summary: str) -> str:
        """
        Generates a chapter outline from a short summary.
        """
        prompt = (
            "Create a detailed chapter outline based on this description:\n\n"
            f"{summary}"
        )
        return self._call_openai(prompt)
