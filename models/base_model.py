"""
Base Model Interface - Abstract class for all AI model implementations.
All model clients must implement this interface for GUI compatibility.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ModelResponse:
    """Standardized response object from any AI model."""
    text: str
    model_used: str
    tokens_used: int = 0
    cost_estimate: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ModelConfig:
    """Configuration for model behavior."""
    max_tokens: int = 4000
    temperature: float = 0.7
    system_prompt: Optional[str] = None


class BaseModel(ABC):
    """
    Abstract base class for AI model implementations.
    Implement this interface for Claude, OpenAI, Gemini, etc.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable model name for GUI display."""
        pass

    @property
    @abstractmethod
    def model_id(self) -> str:
        """API model identifier string."""
        pass

    @property
    @abstractmethod
    def max_context(self) -> int:
        """Maximum context window in tokens."""
        pass

    @property
    @abstractmethod
    def cost_per_million_input(self) -> float:
        """Cost per million input tokens in USD."""
        pass

    @property
    @abstractmethod
    def cost_per_million_output(self) -> float:
        """Cost per million output tokens in USD."""
        pass

    @abstractmethod
    def generate(self, prompt: str, config: Optional[ModelConfig] = None) -> ModelResponse:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The user prompt to send to the model
            config: Optional configuration overrides
            
        Returns:
            ModelResponse with generated text and metadata
        """
        pass

    @abstractmethod
    def review_chapter(
        self,
        chapter_text: str,
        reference_context: str,
        review_type: str = "full",
        config: Optional[ModelConfig] = None
    ) -> ModelResponse:
        """
        Review a chapter with reference context.
        
        Args:
            chapter_text: The chapter content to review
            reference_context: Relevant reference material
            review_type: One of "consistency", "prose", "historical", "full"
            config: Optional configuration overrides
            
        Returns:
            ModelResponse with review feedback
        """
        pass

    @abstractmethod
    def revise_text(
        self,
        original_text: str,
        instructions: str,
        config: Optional[ModelConfig] = None
    ) -> ModelResponse:
        """
        Revise text based on instructions.
        
        Args:
            original_text: Text to revise
            instructions: Revision instructions
            config: Optional configuration overrides
            
        Returns:
            ModelResponse with revised text
        """
        pass

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Uses rough approximation: ~4 characters per token.
        Override for model-specific tokenization.
        """
        return len(text) // 4

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for a request."""
        input_cost = (input_tokens / 1_000_000) * self.cost_per_million_input
        output_cost = (output_tokens / 1_000_000) * self.cost_per_million_output
        return input_cost + output_cost

    def is_available(self) -> bool:
        """Check if model is properly configured and available."""
        return True
