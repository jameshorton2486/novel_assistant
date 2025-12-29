"""
Model Router - Unified interface for multiple AI models.

Supports: Claude Sonnet, Claude Haiku, GPT-4o, Gemini 1.5 Pro

Model Selection Guide:
- Claude Sonnet: Daily chapter work, prose quality (200K context)
- Claude Haiku: Quick consistency checks (200K context)
- GPT-4o: Alternative prose generation (128K context)
- Gemini 1.5 Pro: Full manuscript review (1M context)
"""

import os
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass


class ModelType(Enum):
    CLAUDE_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_HAIKU = "claude-haiku-4-5-20251001"
    GPT_4O = "gpt-4o"
    GEMINI_PRO = "gemini-1.5-pro"


@dataclass
class ModelConfig:
    """Configuration for each model type."""
    name: str
    max_context: int
    best_for: str
    api_key_env: str


MODEL_CONFIGS = {
    ModelType.CLAUDE_SONNET: ModelConfig(
        name="Claude Sonnet",
        max_context=200000,
        best_for="Daily chapter work, prose quality",
        api_key_env="ANTHROPIC_API_KEY"
    ),
    ModelType.CLAUDE_HAIKU: ModelConfig(
        name="Claude Haiku",
        max_context=200000,
        best_for="Quick consistency checks",
        api_key_env="ANTHROPIC_API_KEY"
    ),
    ModelType.GPT_4O: ModelConfig(
        name="GPT-4o",
        max_context=128000,
        best_for="Alternative prose generation",
        api_key_env="OPENAI_API_KEY"
    ),
    ModelType.GEMINI_PRO: ModelConfig(
        name="Gemini 1.5 Pro",
        max_context=1000000,
        best_for="Full manuscript review",
        api_key_env="GOOGLE_API_KEY"
    ),
}


class ModelRouter:
    """
    Routes requests to appropriate AI model based on task type.
    
    Usage:
        router = ModelRouter()
        
        # Generate with default model (Claude Sonnet)
        text = router.generate("Write the opening scene...")
        
        # Use specific model
        text = router.generate("Write...", model=ModelType.GPT_4O)
        
        # Quick check with Haiku
        issues = router.quick_check(chapter_text, "era_language")
        
        # Full manuscript review with Gemini
        report = router.batch_review(all_chapters)
    """
    
    def __init__(self, system_prompt: str = ""):
        self.system_prompt = system_prompt
        self.clients = {}
        self._init_clients()
        
    def _init_clients(self):
        """Initialize available model clients based on API keys."""
        # Claude (Anthropic)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                from anthropic import Anthropic
                self.clients["anthropic"] = Anthropic(api_key=anthropic_key)
            except ImportError:
                print("Warning: anthropic package not installed")
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.clients["openai"] = OpenAI(api_key=openai_key)
            except ImportError:
                print("Warning: openai package not installed")
        
        # Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                self.clients["google"] = genai
            except ImportError:
                print("Warning: google-generativeai package not installed")
    
    def get_available_models(self) -> List[ModelType]:
        """Return list of models with valid API keys configured."""
        available = []
        
        if "anthropic" in self.clients:
            available.extend([ModelType.CLAUDE_SONNET, ModelType.CLAUDE_HAIKU])
        if "openai" in self.clients:
            available.append(ModelType.GPT_4O)
        if "google" in self.clients:
            available.append(ModelType.GEMINI_PRO)
            
        return available
    
    def _call_claude(self, prompt: str, model: ModelType, 
                     max_tokens: int = 2000) -> str:
        """Call Claude API."""
        if "anthropic" not in self.clients:
            raise ValueError("Anthropic API key not configured")
            
        response = self.clients["anthropic"].messages.create(
            model=model.value,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if response.content:
            return response.content[0].text
        return "[No response from Claude]"
    
    def _call_openai(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call OpenAI API."""
        if "openai" not in self.clients:
            raise ValueError("OpenAI API key not configured")
            
        response = self.clients["openai"].chat.completions.create(
            model=ModelType.GPT_4O.value,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        if response.choices:
            return response.choices[0].message.content
        return "[No response from OpenAI]"
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        if "google" not in self.clients:
            raise ValueError("Google API key not configured")
            
        model = self.clients["google"].GenerativeModel(ModelType.GEMINI_PRO.value)
        
        full_prompt = f"{self.system_prompt}\n\n{prompt}" if self.system_prompt else prompt
        response = model.generate_content(full_prompt)
        
        return response.text if response.text else "[No response from Gemini]"
    
    def generate(self, prompt: str, model: ModelType = ModelType.CLAUDE_SONNET,
                 max_tokens: int = 2000) -> str:
        """
        Generate text using specified model.
        
        Args:
            prompt: The generation prompt
            model: Which model to use (default: Claude Sonnet)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        try:
            if model in [ModelType.CLAUDE_SONNET, ModelType.CLAUDE_HAIKU]:
                return self._call_claude(prompt, model, max_tokens)
            elif model == ModelType.GPT_4O:
                return self._call_openai(prompt, max_tokens)
            elif model == ModelType.GEMINI_PRO:
                return self._call_gemini(prompt)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            return f"[Error: {str(e)}]"
    
    def revise(self, text: str, instructions: str,
               model: ModelType = ModelType.CLAUDE_SONNET) -> str:
        """
        Revise text using specified model.
        
        Args:
            text: Original text to revise
            instructions: Revision instructions
            model: Which model to use
            
        Returns:
            Revised text
        """
        prompt = (
            "Revise the following text according to the instructions.\n"
            "Preserve meaning unless explicitly told otherwise.\n\n"
            f"INSTRUCTIONS:\n{instructions}\n\n"
            f"ORIGINAL TEXT:\n{text}"
        )
        return self.generate(prompt, model)
    
    def batch_review(self, chapters: List[Dict], 
                     model: ModelType = ModelType.GEMINI_PRO) -> Dict:
        """
        Review multiple chapters at once.
        Best used with Gemini for its 1M token context.
        
        Args:
            chapters: List of {"name": str, "content": str}
            model: Model to use (default: Gemini for large context)
            
        Returns:
            Review report with findings per chapter
        """
        # Combine chapters for review
        combined = "\n\n---\n\n".join([
            f"# {ch['name']}\n\n{ch['content']}" 
            for ch in chapters
        ])
        
        prompt = (
            "Review the following manuscript chapters for:\n"
            "1. Consistency issues (character details, timeline, locations)\n"
            "2. Pacing problems (tension drops, slow sections)\n"
            "3. Voice inconsistencies\n"
            "4. Plot holes or continuity errors\n\n"
            "Provide a structured report with specific citations.\n\n"
            f"MANUSCRIPT:\n\n{combined}"
        )
        
        response = self.generate(prompt, model, max_tokens=4000)
        
        return {
            "model_used": model.value,
            "chapters_reviewed": len(chapters),
            "report": response
        }
    
    def quick_check(self, text: str, check_type: str,
                    model: ModelType = ModelType.CLAUDE_HAIKU) -> Dict:
        """
        Quick consistency/style check using fast model.
        
        Args:
            text: Text to check
            check_type: Type of check ("era_language", "consistency", "pacing")
            model: Model to use (default: Haiku for speed)
            
        Returns:
            Check results with flagged issues
        """
        check_prompts = {
            "era_language": (
                "Check this 1950s-era text for anachronistic language.\n"
                "Flag any modern terms, therapy-speak, or corporate jargon.\n"
                "Return a JSON list of {term, line, suggestion}.\n\n"
            ),
            "consistency": (
                "Check for internal consistency issues:\n"
                "- Character names/ages/descriptions\n"
                "- Timeline/dates\n"
                "- Location details\n"
                "Return a JSON list of {issue, location, severity}.\n\n"
            ),
            "pacing": (
                "Analyze the pacing of this text:\n"
                "- Flag sections where tension drops\n"
                "- Identify slow/draggy passages\n"
                "- Note abrupt transitions\n"
                "Return a JSON list of {issue, location, suggestion}.\n\n"
            )
        }
        
        if check_type not in check_prompts:
            raise ValueError(f"Unknown check type: {check_type}")
        
        prompt = check_prompts[check_type] + f"TEXT:\n{text}"
        response = self.generate(prompt, model, max_tokens=1000)
        
        return {
            "check_type": check_type,
            "model_used": model.value,
            "results": response
        }
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt used for all calls."""
        self.system_prompt = prompt
