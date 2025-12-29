"""
Claude Model Implementation - Anthropic Claude API wrapper.
Implements BaseModel interface for GUI integration.
"""

import os
from typing import Optional

try:
    from anthropic import Anthropic, APIError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from models.base_model import BaseModel, ModelResponse, ModelConfig


# Review prompts for different review types
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


class ClaudeModel(BaseModel):
    """Claude API implementation using Anthropic SDK."""

    def __init__(self, model_variant: str = "sonnet"):
        """
        Initialize Claude client.
        
        Args:
            model_variant: "sonnet", "opus", or "haiku"
        """
        self._variant = model_variant
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            return
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self._client = Anthropic(api_key=api_key)

    @property
    def name(self) -> str:
        variants = {
            "sonnet": "Claude Sonnet 4",
            "opus": "Claude Opus 4.5",
            "haiku": "Claude Haiku 4.5"
        }
        return variants.get(self._variant, "Claude Sonnet 4")

    @property
    def model_id(self) -> str:
        variants = {
            "sonnet": "claude-sonnet-4-20250514",
            "opus": "claude-opus-4-5-20250101",
            "haiku": "claude-haiku-4-5-20250101"
        }
        return variants.get(self._variant, "claude-sonnet-4-20250514")

    @property
    def max_context(self) -> int:
        return 200000  # 200K for all Claude 4 models

    @property
    def cost_per_million_input(self) -> float:
        costs = {
            "sonnet": 3.0,
            "opus": 15.0,
            "haiku": 0.80
        }
        return costs.get(self._variant, 3.0)

    @property
    def cost_per_million_output(self) -> float:
        costs = {
            "sonnet": 15.0,
            "opus": 75.0,
            "haiku": 4.0
        }
        return costs.get(self._variant, 15.0)

    def is_available(self) -> bool:
        """Check if Claude is properly configured."""
        return ANTHROPIC_AVAILABLE and self._client is not None

    def generate(self, prompt: str, config: Optional[ModelConfig] = None) -> ModelResponse:
        """Generate text using Claude."""
        if not self.is_available():
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message="Claude API not configured. Set ANTHROPIC_API_KEY environment variable."
            )

        config = config or ModelConfig()
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model_id,
                "max_tokens": config.max_tokens,
                "messages": messages
            }
            
            if config.system_prompt:
                kwargs["system"] = config.system_prompt

            response = self._client.messages.create(**kwargs)
            
            text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            return ModelResponse(
                text=text,
                model_used=self.model_id,
                tokens_used=input_tokens + output_tokens,
                cost_estimate=self.estimate_cost(input_tokens, output_tokens),
                success=True
            )

        except APIError as e:
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message=f"Claude API error: {str(e)}"
            )
        except Exception as e:
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message=f"Unexpected error: {str(e)}"
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


# Factory function for easy instantiation
def create_claude_model(variant: str = "sonnet") -> ClaudeModel:
    """Create a Claude model instance."""
    return ClaudeModel(model_variant=variant)
