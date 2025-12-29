"""
Gemini Model Implementation - Google Gemini API wrapper.
Implements BaseModel interface for GUI integration.

Gemini 1.5 Pro has a 1M token context - ideal for full manuscript analysis.
"""

import os
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from models.base_model import BaseModel, ModelResponse, ModelConfig


# Review prompts (same structure for consistency)
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

Provide a structured review with specific, actionable feedback. Prioritize the most critical issues first.""",

    "manuscript_audit": """You are conducting a full manuscript audit. With access to the complete novel, analyze:

1. GLOBAL CONSISTENCY
   - Character arcs across all chapters
   - Timeline coherence from start to finish
   - Subplot tracking and resolution
   - Foreshadowing payoffs
   
2. STRUCTURAL ANALYSIS
   - Pacing across the full narrative
   - Scene distribution and balance
   - Chapter length consistency
   - Act structure adherence
   
3. VOICE & STYLE
   - Consistency of narrative voice
   - POV adherence
   - Tone shifts (intentional vs. accidental)
   
4. THEMATIC COHERENCE
   - Theme development across chapters
   - Symbol/motif tracking
   - Resolution of thematic questions

Provide a comprehensive report with chapter-specific citations."""
}


class GeminiModel(BaseModel):
    """Google Gemini API implementation."""

    def __init__(self, model_variant: str = "gemini-1.5-pro"):
        """
        Initialize Gemini client.
        
        Args:
            model_variant: "gemini-1.5-pro", "gemini-1.5-flash", or "gemini-2.0-flash"
        """
        self._variant = model_variant
        self._model = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Gemini client."""
        if not GEMINI_AVAILABLE:
            return
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self._variant)

    @property
    def name(self) -> str:
        variants = {
            "gemini-1.5-pro": "Gemini 1.5 Pro (1M context)",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-2.0-flash": "Gemini 2.0 Flash"
        }
        return variants.get(self._variant, "Gemini 1.5 Pro")

    @property
    def model_id(self) -> str:
        return self._variant

    @property
    def max_context(self) -> int:
        contexts = {
            "gemini-1.5-pro": 1000000,  # 1M tokens!
            "gemini-1.5-flash": 1000000,
            "gemini-2.0-flash": 1000000
        }
        return contexts.get(self._variant, 1000000)

    @property
    def cost_per_million_input(self) -> float:
        costs = {
            "gemini-1.5-pro": 1.25,
            "gemini-1.5-flash": 0.075,
            "gemini-2.0-flash": 0.10
        }
        return costs.get(self._variant, 1.25)

    @property
    def cost_per_million_output(self) -> float:
        costs = {
            "gemini-1.5-pro": 5.0,
            "gemini-1.5-flash": 0.30,
            "gemini-2.0-flash": 0.40
        }
        return costs.get(self._variant, 5.0)

    def is_available(self) -> bool:
        """Check if Gemini is properly configured."""
        return GEMINI_AVAILABLE and self._model is not None

    def generate(self, prompt: str, config: Optional[ModelConfig] = None) -> ModelResponse:
        """Generate text using Gemini."""
        if not self.is_available():
            return ModelResponse(
                text="",
                model_used=self.model_id,
                success=False,
                error_message="Gemini API not configured. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
            )

        config = config or ModelConfig()
        
        try:
            # Build the full prompt with system context if provided
            full_prompt = prompt
            if config.system_prompt:
                full_prompt = f"{config.system_prompt}\n\n{prompt}"

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=config.max_tokens,
                temperature=config.temperature
            )

            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            text = response.text if response.text else ""
            
            # Gemini doesn't always return token counts in the same way
            # Estimate based on text length
            input_tokens = self.estimate_tokens(full_prompt)
            output_tokens = self.estimate_tokens(text)
            
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
                error_message=f"Gemini API error: {str(e)}"
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

    def review_full_manuscript(
        self,
        chapters: list[str],
        reference_context: str,
        config: Optional[ModelConfig] = None
    ) -> ModelResponse:
        """
        Review the entire manuscript at once.
        Gemini's 1M context makes this possible.
        
        Args:
            chapters: List of chapter texts in order
            reference_context: All reference material
            config: Optional configuration
            
        Returns:
            ModelResponse with comprehensive manuscript review
        """
        system_prompt = REVIEW_PROMPTS["manuscript_audit"]
        
        # Build full manuscript text
        manuscript_parts = []
        for i, chapter in enumerate(chapters, 1):
            manuscript_parts.append(f"=== CHAPTER {i} ===\n{chapter}")
        
        full_manuscript = "\n\n".join(manuscript_parts)
        
        prompt = f"""## REFERENCE MATERIAL
{reference_context}

## COMPLETE MANUSCRIPT
{full_manuscript}

## INSTRUCTIONS
Conduct a comprehensive manuscript audit. You have access to the full novel.
Analyze cross-chapter consistency, character arcs, timeline coherence, and thematic development.
Be specific with chapter and passage citations."""

        config = config or ModelConfig()
        config.system_prompt = system_prompt
        config.max_tokens = 8000  # Larger output for full manuscript review
        
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
def create_gemini_model(variant: str = "gemini-1.5-pro") -> GeminiModel:
    """Create a Gemini model instance."""
    return GeminiModel(model_variant=variant)
