"""
OpenAI Model Implementation - GPT API wrapper.
Implements BaseModel interface for GUI integration.
"""

import os
from typing import Optional

try:
    from openai import OpenAI, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from models.base_model import BaseModel, ModelResponse, ModelConfig


# Review prompts (same structure as Claude for consistency)
REVIEW_PROMPTS = {
    "consistency": """You are a continuity editor. Review this chapter for:
- Character name consistency and descriptions
- Timeline accuracy (dates, ages, sequences)
- Location details matching previous mentions
- Object/prop consistency
- Dialogue attribution accuracy

Reference material is provided for verification. Flag any inconsistencies with specific quotes and corrections.

Be concise. List issues as bullet points with page/paragraph references.""",

    "prose": """You are a literary editor reviewing prose quality. Evaluate:
- Sentence rhythm and flow
- Word choice precision
- Show vs. tell balance
- Dialogue naturalness
- Pacing within scenes
- Sensory details
- Voice consistency

Provide specific suggestions with examples. Focus on the 3-5 most impactful improvements.""",

    "historical": """You are a historical accuracy consultant for 1950s America. Verify:
- Period-accurate language and slang
- Technology and objects appropriate to the era
- Social customs and attitudes
- Prices, wages, and costs
- Cultural references
- Historical events mentioned

Flag anachronisms with corrections. Reference the provided historical context.""",

    "full": """You are a developmental editor conducting a comprehensive chapter review. Evaluate:

1. CONTINUITY: Character details, timeline, locations, objects
2. PROSE QUALITY: Rhythm, word choice, pacing, voice
3. HISTORICAL ACCURACY: Period details, language, customs
4. NARRATIVE: Arc progression, tension, emotional beats
5. DIALOGUE: Authenticity, subtext, character voice

Provide a structured review with specific, actionable feedback. Prioritize the most critical issues first."""
}


class OpenAIModel(BaseModel):
    """OpenAI GPT API implementation."""

    def __init__(self, model_variant: str = "gpt-4o"):
        """
        Initialize OpenAI client.
        
        Args:
            model_variant: "gpt-4o", "gpt-4o-mini", or "gpt-4-turbo"
        """
        self._variant = model_variant
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client."""
        if not OPENAI_AVAILABLE:
            return
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self._client = OpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        variants = {
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4-turbo": "GPT-4 Turbo"
        }
        return variants.get(self._variant, "GPT-4o")

    @property
    def model_id(self) -> str:
        return self._variant

    @property
    def max_context(self) -> int:
        contexts = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000
        }
        return contexts.get(self._variant, 128000)

    @property
    def cost_per_million_input(self) -> float:
        costs = {
            "gpt-4o": 2.50,
            "gpt-4o-mini": 0.15,
            "gpt-4-turbo": 10.0
        }
        return costs.get(self._variant, 2.50)

    @property
    def cost_per_million_output(self) -> float:
        costs = {
            "gpt-4o": 10.0,
            "gpt-4o-mini": 0.60,
            "gpt-4-turbo": 30.0
        }
        return costs.get(self._variant, 10.0)

    def is_available(self) -> bool:
        """Check if OpenAI is properly configured."""
        return OPENAI_AVAILABLE and self._client is not None

    def generate(self, prompt: str, config: Optional[ModelConfig] = None) -> ModelResponse:
        """Generate text using GPT."""
        if not self.is_available():
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message="OpenAI API not configured. Set OPENAI_API_KEY environment variable."
            )

        config = config or ModelConfig()
        
        try:
            messages = []
            
            if config.system_prompt:
                messages.append({"role": "system", "content": config.system_prompt})
            
            messages.append({"role": "user", "content": prompt})

            response = self._client.chat.completions.create(
                model=self.model_id,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=messages
            )
            
            text = response.choices[0].message.content if response.choices else ""
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            
            return ModelResponse(
                text=text,
                model_used=self.model_id,
                tokens_used=input_tokens + output_tokens,
                cost_estimate=self.estimate_cost(input_tokens, output_tokens),
                success=True
            )

        except Exception as e:
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message=f"OpenAI API error: {str(e)}"
            )

    def review_chapter(
        self,
        chapter_text: str,
        reference_context: str,
        review_type: str = "full",
        config: Optional[ModelConfig] = None
    ) -> ModelResponse:
        """Review a chapter with reference context."""
        
        system_prompt = REVIEW_PROMPTS.get(review_type, REVIEW_PROMPTS["full"])
        
        prompt = f"""## REFERENCE CONTEXT
{reference_context}

## CHAPTER TO REVIEW
{chapter_text}

## INSTRUCTIONS
Conduct a {review_type} review of this chapter using the reference context provided.
Be specific, cite passages, and provide actionable feedback."""

        config = config or ModelConfig()
        config.system_prompt = system_prompt
        config.max_tokens = 4000
        
        return self.generate(prompt, config)

    def revise_text(
        self,
        original_text: str,
        instructions: str,
        config: Optional[ModelConfig] = None
    ) -> ModelResponse:
        """Revise text based on instructions."""
        
        system_prompt = """You are a skilled literary editor. Revise the provided text according to the instructions while:
- Preserving the author's voice and style
- Maintaining narrative continuity
- Keeping character authenticity
- Only changing what's explicitly requested

Output ONLY the revised text, no explanations or meta-commentary."""

        prompt = f"""## REVISION INSTRUCTIONS
{instructions}

## ORIGINAL TEXT
{original_text}

## OUTPUT
Provide the revised text:"""

        config = config or ModelConfig()
        config.system_prompt = system_prompt
        
        return self.generate(prompt, config)


# Factory function
def create_openai_model(variant: str = "gpt-4o") -> OpenAIModel:
    """Create an OpenAI model instance."""
    return OpenAIModel(model_variant=variant)
