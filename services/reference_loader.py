"""
Reference Loader with Research Governance
==========================================

Loads reference material according to the four-class governance model.

GOVERNANCE RULES:
- CANON: Always loaded, never contradicted
- CONTEXT: Loaded for plausibility, never narrated
- ARTIFACT: Loaded for specific scene triggers only
- CRAFT: Loaded for revision mode only

The loader enforces these rules by controlling WHAT is loaded WHEN.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .research_ingest import ResearchClass


class LoadingContext(Enum):
    """Context in which reference material is being loaded."""
    DRAFTING = "drafting"           # Writing new content
    REVISION = "revision"           # Editing existing content
    CONSISTENCY_CHECK = "consistency"  # Checking facts
    STYLE_CHECK = "style"           # Checking voice/prose
    SCENE_DEVELOPMENT = "scene"     # Developing specific scene
    FULL_CONTEXT = "full"           # Load everything available


@dataclass
class LoadedReference:
    """Bundle of loaded reference material."""
    canon: str          # Always included
    context: str        # Included based on context
    artifacts: str      # Included only for scene development
    craft: str          # Included only for revision/style
    total_tokens: int
    sources_loaded: List[str]


class ReferenceLoader:
    """
    Governance-aware reference loading.
    
    Controls what material is available to the AI based on:
    1. The research class of each document
    2. The current working context
    3. Token budget constraints
    
    This prevents misuse of reference material.
    """
    
    # What to load in each context
    CONTEXT_RULES = {
        LoadingContext.DRAFTING: {
            ResearchClass.CANON: True,      # Always need facts
            ResearchClass.CONTEXT: True,    # Need background
            ResearchClass.ARTIFACT: False,  # Only load specific artifacts
            ResearchClass.CRAFT: False,     # Style guide only, not process
        },
        LoadingContext.REVISION: {
            ResearchClass.CANON: True,
            ResearchClass.CONTEXT: False,   # Focus on text, not background
            ResearchClass.ARTIFACT: False,
            ResearchClass.CRAFT: True,      # Need style rules
        },
        LoadingContext.CONSISTENCY_CHECK: {
            ResearchClass.CANON: True,      # Primary focus
            ResearchClass.CONTEXT: True,    # For plausibility
            ResearchClass.ARTIFACT: False,
            ResearchClass.CRAFT: False,
        },
        LoadingContext.STYLE_CHECK: {
            ResearchClass.CANON: False,     # Not checking facts
            ResearchClass.CONTEXT: False,
            ResearchClass.ARTIFACT: False,
            ResearchClass.CRAFT: True,      # Primary focus
        },
        LoadingContext.SCENE_DEVELOPMENT: {
            ResearchClass.CANON: True,
            ResearchClass.CONTEXT: True,
            ResearchClass.ARTIFACT: True,   # Artifacts can trigger scenes
            ResearchClass.CRAFT: False,
        },
        LoadingContext.FULL_CONTEXT: {
            ResearchClass.CANON: True,
            ResearchClass.CONTEXT: True,
            ResearchClass.ARTIFACT: True,
            ResearchClass.CRAFT: True,
        },
    }
    
    # Headers that explain how to use each class
    CLASS_HEADERS = {
        ResearchClass.CANON: """
# CANON REFERENCE (Authoritative)
The following facts are ESTABLISHED in the novel. They cannot be contradicted.
Use these as constraints. If something conflicts with canon, canon wins.
""",
        ResearchClass.CONTEXT: """
# CONTEXTUAL BACKGROUND (Non-Authoritative)
The following provides historical/cultural context. Use for plausibility checks.
NEVER narrate this information directly to the reader.
This is pressure, not content.
""",
        ResearchClass.ARTIFACT: """
# ARTIFACTS (Scene Triggers)
The following are in-world documents that can trigger scenes or memories.
Experience these through character POV. Meaning comes from contrast, not exposition.
NEVER summarize these generically.
""",
        ResearchClass.CRAFT: """
# CRAFT GUIDANCE (Editorial Only)
The following guides HOW to write, not WHAT to write.
Apply during revision. Never inject into narrative.
This is scaffolding, not story material.
"""
    }
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.reference_dir = self.base_dir / "reference"
        self.research_dir = self.base_dir / "research"
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate."""
        return len(text) // 4
    
    def _load_directory(self, directory: Path, pattern: str = "*.md") -> str:
        """Load all matching files from a directory."""
        if not directory.exists():
            return ""
        
        content = []
        for filepath in sorted(directory.rglob(pattern)):
            if filepath.is_file():
                try:
                    text = filepath.read_text(encoding='utf-8')
                    content.append(f"\n## {filepath.stem}\n\n{text}")
                except Exception:
                    continue
        
        return "\n".join(content)
    
    def _load_canon(self) -> str:
        """Load canon reference material."""
        # Canon lives in reference/canon/
        content = []
        canon_dir = self.reference_dir / "canon"
        
        # Core canon files
        core_files = [
            "MASTER_CANON.md",
        ]
        
        for filename in core_files:
            filepath = canon_dir / filename
            if filepath.exists():
                content.append(filepath.read_text(encoding='utf-8'))
        
        # Timeline
        timeline_file = canon_dir / "timeline" / "master_timeline.md"
        if timeline_file.exists():
            content.append("\n## Timeline\n")
            content.append(timeline_file.read_text(encoding='utf-8'))
        
        # Plot
        plot_file = canon_dir / "plot" / "chapter_beats.md"
        if plot_file.exists():
            content.append("\n## Plot Structure\n")
            content.append(plot_file.read_text(encoding='utf-8'))
        
        # Character files
        chars_dir = canon_dir / "characters"
        if chars_dir.exists():
            content.append("\n## Characters\n")
            content.append(self._load_directory(chars_dir))
        
        # Relationships
        relationships_file = canon_dir / "relationships" / "relationship_map.md"
        if relationships_file.exists():
            content.append("\n## Relationships\n")
            content.append(relationships_file.read_text(encoding='utf-8'))
        
        return "\n\n".join(content)
    
    def _load_context(self) -> str:
        """Load contextual research material."""
        # Context lives in reference/context/
        context_dir = self.reference_dir / "context"
        
        # Load master historical context
        master_context = context_dir / "HISTORICAL_CONTEXT.md"
        content = []
        if master_context.exists():
            content.append(master_context.read_text(encoding='utf-8'))
        
        # Load subdirectories
        subdirs = ["circus_life", "bracero_program", "civil_rights", "social_backdrop"]
        for subdir in subdirs:
            subdir_path = context_dir / subdir
            if subdir_path.exists():
                content.append(f"\n## {subdir.replace('_', ' ').title()}\n")
                content.append(self._load_directory(subdir_path))
        
        return "\n\n".join(content)
    
    def _load_artifacts(self, artifact_ids: List[str] = None) -> str:
        """Load artifact material, optionally filtered."""
        # Artifacts live in reference/artifacts/
        artifacts_dir = self.reference_dir / "artifacts"
        
        if not artifacts_dir.exists():
            return ""
        
        # Load artifact index
        content = []
        index_file = artifacts_dir / "ARTIFACT_INDEX.md"
        if index_file.exists():
            content.append(index_file.read_text(encoding='utf-8'))
        
        if artifact_ids:
            # Load specific artifacts
            for aid in artifact_ids:
                for filepath in artifacts_dir.rglob(f"*{aid}*"):
                    if filepath.is_file() and filepath.name != "ARTIFACT_INDEX.md":
                        content.append(filepath.read_text(encoding='utf-8'))
            return "\n\n".join(content)
        else:
            # Load postcards and letters directories
            for subdir in ["postcards", "letters"]:
                subdir_path = artifacts_dir / subdir
                if subdir_path.exists():
                    content.append(self._load_directory(subdir_path))
            return "\n\n".join(content)
    
    def _load_craft(self) -> str:
        """Load craft guidance material."""
        # Craft lives in reference/craft/
        content = []
        craft_dir = self.reference_dir / "craft"
        
        # Style charter is primary craft document
        style_charter = craft_dir / "STYLE_CHARTER.md"
        if style_charter.exists():
            content.append(style_charter.read_text(encoding='utf-8'))
        
        # Vocabulary directory
        vocab_dir = craft_dir / "vocabulary"
        if vocab_dir.exists():
            content.append("\n## Vocabulary\n")
            content.append(self._load_directory(vocab_dir))
        
        # Scene checklist
        scene_checklist = craft_dir / "scene_checklist.md"
        if scene_checklist.exists():
            content.append("\n## Scene Checklist\n")
            content.append(scene_checklist.read_text(encoding='utf-8'))
        
        return "\n\n".join(content)
    
    def load_for_context(
        self,
        context: LoadingContext,
        chapter_num: Optional[int] = None,
        characters: List[str] = None,
        artifact_ids: List[str] = None,
        max_tokens: int = 50000
    ) -> LoadedReference:
        """
        Load reference material appropriate for the given context.
        
        Args:
            context: What the reference will be used for
            chapter_num: Specific chapter (for focused loading)
            characters: Specific characters to include
            artifact_ids: Specific artifacts to include
            max_tokens: Budget limit
        
        Returns:
            LoadedReference with governed material
        """
        rules = self.CONTEXT_RULES[context]
        sources = []
        
        # Build each section based on rules
        canon_text = ""
        context_text = ""
        artifacts_text = ""
        craft_text = ""
        
        if rules[ResearchClass.CANON]:
            canon_text = self._load_canon()
            if canon_text:
                canon_text = self.CLASS_HEADERS[ResearchClass.CANON] + canon_text
                sources.append("canon")
        
        if rules[ResearchClass.CONTEXT]:
            context_text = self._load_context()
            if context_text:
                context_text = self.CLASS_HEADERS[ResearchClass.CONTEXT] + context_text
                sources.append("context")
        
        if rules[ResearchClass.ARTIFACT]:
            artifacts_text = self._load_artifacts(artifact_ids)
            if artifacts_text:
                artifacts_text = self.CLASS_HEADERS[ResearchClass.ARTIFACT] + artifacts_text
                sources.append("artifacts")
        
        if rules[ResearchClass.CRAFT]:
            craft_text = self._load_craft()
            if craft_text:
                craft_text = self.CLASS_HEADERS[ResearchClass.CRAFT] + craft_text
                sources.append("craft")
        
        # Calculate tokens
        total_tokens = sum([
            self._estimate_tokens(canon_text),
            self._estimate_tokens(context_text),
            self._estimate_tokens(artifacts_text),
            self._estimate_tokens(craft_text)
        ])
        
        # Truncate if over budget (prioritize canon > craft > context > artifacts)
        if total_tokens > max_tokens:
            # Simple truncation strategy
            remaining = max_tokens
            
            canon_tokens = self._estimate_tokens(canon_text)
            if canon_tokens <= remaining:
                remaining -= canon_tokens
            else:
                canon_text = canon_text[:remaining * 4]
                remaining = 0
            
            if remaining > 0:
                craft_tokens = self._estimate_tokens(craft_text)
                if craft_tokens <= remaining:
                    remaining -= craft_tokens
                else:
                    craft_text = craft_text[:remaining * 4]
                    remaining = 0
            else:
                craft_text = ""
            
            if remaining > 0:
                context_tokens = self._estimate_tokens(context_text)
                if context_tokens <= remaining:
                    remaining -= context_tokens
                else:
                    context_text = context_text[:remaining * 4]
                    remaining = 0
            else:
                context_text = ""
            
            if remaining > 0:
                artifacts_text = artifacts_text[:remaining * 4]
            else:
                artifacts_text = ""
            
            total_tokens = max_tokens
        
        return LoadedReference(
            canon=canon_text,
            context=context_text,
            artifacts=artifacts_text,
            craft=craft_text,
            total_tokens=total_tokens,
            sources_loaded=sources
        )
    
    def load_for_chapter(self, chapter_num: int) -> LoadedReference:
        """Load reference for drafting a specific chapter."""
        return self.load_for_context(
            LoadingContext.DRAFTING,
            chapter_num=chapter_num
        )
    
    def load_for_revision(self) -> LoadedReference:
        """Load reference for revision mode."""
        return self.load_for_context(LoadingContext.REVISION)
    
    def load_for_consistency(self) -> LoadedReference:
        """Load reference for consistency checking."""
        return self.load_for_context(LoadingContext.CONSISTENCY_CHECK)
    
    def load_for_style(self) -> LoadedReference:
        """Load reference for style checking."""
        return self.load_for_context(LoadingContext.STYLE_CHECK)
    
    def get_combined_reference(self, loaded: LoadedReference) -> str:
        """Combine loaded reference into a single string for AI."""
        sections = []
        
        if loaded.canon:
            sections.append(loaded.canon)
        if loaded.context:
            sections.append(loaded.context)
        if loaded.artifacts:
            sections.append(loaded.artifacts)
        if loaded.craft:
            sections.append(loaded.craft)
        
        if not sections:
            return "[No reference material loaded for this context]"
        
        return "\n\n---\n\n".join(sections)


# Convenience functions

def load_reference(
    context: str,
    base_dir: str = ".",
    max_tokens: int = 50000
) -> str:
    """
    Load governed reference material.
    
    Args:
        context: One of: drafting, revision, consistency, style, scene, full
        base_dir: Application root
        max_tokens: Token budget
    
    Returns:
        Combined reference text with governance headers
    """
    loader = ReferenceLoader(Path(base_dir))
    ctx = LoadingContext(context)
    loaded = loader.load_for_context(ctx, max_tokens=max_tokens)
    return loader.get_combined_reference(loaded)


def get_loading_contexts() -> List[Dict]:
    """Get available loading contexts for UI."""
    return [
        {
            "value": ctx.value,
            "name": ctx.name.replace("_", " ").title(),
            "loads": {
                rc.value: include 
                for rc, include in ReferenceLoader.CONTEXT_RULES[ctx].items()
            }
        }
        for ctx in LoadingContext
    ]
