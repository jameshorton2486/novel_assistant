"""
Research Classifier Service
============================

AI-powered classification of research documents into four classes.

CRITICAL: Classification happens FIRST, before any summarization.
The class determines how the document will be processed and used.

Four Classes:
1. CANON - Sacred facts for the novel
2. CONTEXT - Background material (pressure, not content)
3. ARTIFACT - Scene triggers (letters, postcards, ephemera)
4. CRAFT - Writing guidance (style, process)

The AI helps decide what matters. The human decides what is true.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .research_ingest import ResearchClass, RESEARCH_CLASS_INFO


@dataclass
class ClassificationResult:
    """Result of AI classification."""
    primary_class: ResearchClass
    confidence: float  # 0.0 - 1.0
    subtype: Optional[str]
    reasoning: str
    alternative_class: Optional[ResearchClass]
    key_indicators: List[str]


class ResearchClassifier:
    """
    Classifies research documents into the four governance classes.
    
    Classification must happen BEFORE distillation because:
    - Canon documents are distilled differently than Context
    - Artifacts should never be summarized
    - Craft documents need different extraction rules
    """
    
    CLASSIFICATION_PROMPT = """You are a research librarian for a 1950s historical fiction novel.

TASK: Classify this document into ONE of four research classes.

THE FOUR CLASSES:

1. CANON (novel-bound, sacred)
   - Facts that will appear on the page
   - Timeline dates, character details, relationships
   - Historical events explicitly referenced in narrative
   - Rules governing the novel (no modern slang, etc.)
   - Example: "Character bible with Tommy's age, Jenny's backstory"

2. CONTEXT (background, non-authoritative)
   - Historical accuracy material NOT directly quoted
   - Background that informs but isn't narrated
   - Social climate, attitudes, newspaper tone
   - Research the author uses but reader never sees directly
   - Example: "Academic paper on bracero program conditions"

3. ARTIFACT (trigger material, scene devices)
   - Documents that exist INSIDE the story world
   - Letters, postcards, ticket stubs, programs
   - Things characters could hold or reference
   - Memory triggers, not data
   - Example: "Reproduction of 1954 circus program"

4. CRAFT (meta-guidance, editorial)
   - Material about HOW to write, not WHAT happened
   - Style guides, author influences
   - Process documents, workflow notes
   - Never enters the narrative
   - Example: "Analysis of Hemingway's prose style"

DOCUMENT TO CLASSIFY:

Filename: {filename}
Content Preview:
---
{content_preview}
---

RESPOND IN JSON FORMAT ONLY:
{{
    "primary_class": "canon|context|artifact|craft",
    "confidence": 0.0-1.0,
    "subtype": "specific category or null",
    "reasoning": "one sentence explanation",
    "alternative_class": "second most likely class or null",
    "key_indicators": ["indicator1", "indicator2", "indicator3"]
}}

Classify based on HOW this document should be USED, not just what it contains.
"""
    
    # Subtypes for each class
    SUBTYPES = {
        ResearchClass.CANON: [
            "characters",      # Character bibles, profiles
            "timeline",        # Dates, events, sequence
            "locations",       # Places in the novel
            "terminology",     # Period-appropriate language
            "rules",           # Novel constraints
        ],
        ResearchClass.CONTEXT: [
            "historical",      # Period history
            "social",          # Social attitudes, culture
            "operational",     # How things worked (circus, labor)
            "geographic",      # Places, routes, climate
        ],
        ResearchClass.ARTIFACT: [
            "letters",         # Correspondence
            "postcards",       # Visual ephemera
            "programs",        # Circus programs, handbills
            "photographs",     # Described images
            "documents",       # Contracts, certificates
        ],
        ResearchClass.CRAFT: [
            "style",           # Voice, prose guidance
            "structure",       # Plot, pacing, beats
            "process",         # Workflow, routine
            "influences",      # Author models
        ]
    }
    
    def __init__(self, base_dir: Path, model_client=None):
        self.base_dir = Path(base_dir)
        self.model_client = model_client
    
    def _read_document(self, filepath: Path) -> str:
        """Read document content."""
        suffix = filepath.suffix.lower()
        
        if suffix in ['.md', '.txt']:
            return filepath.read_text(encoding='utf-8')
        
        elif suffix == '.docx':
            try:
                from docx import Document
                doc = Document(filepath)
                return '\n\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
            except ImportError:
                return "[DOCX reading requires python-docx]"
        
        elif suffix == '.pdf':
            try:
                import fitz
                doc = fitz.open(filepath)
                return '\n\n'.join([page.get_text() for page in doc])
            except ImportError:
                return "[PDF reading requires PyMuPDF]"
        
        return "[Unsupported format]"
    
    def _keyword_based_classification(self, content: str, filename: str) -> ClassificationResult:
        """Fallback classification using keyword analysis."""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Score each class
        scores = {rc: 0 for rc in ResearchClass}
        indicators = {rc: [] for rc in ResearchClass}
        
        # Canon indicators
        canon_keywords = ['character', 'timeline', 'chapter', 'bible', 'profile', 
                         'canon', 'must', 'rule', 'constraint', 'age:', 'born:']
        for kw in canon_keywords:
            if kw in content_lower or kw in filename_lower:
                scores[ResearchClass.CANON] += 1
                indicators[ResearchClass.CANON].append(kw)
        
        # Context indicators
        context_keywords = ['history', 'historical', 'program', 'operation', 
                          'research', 'study', 'analysis', 'report', 'conditions',
                          'bracero', 'immigration', 'labor']
        for kw in context_keywords:
            if kw in content_lower or kw in filename_lower:
                scores[ResearchClass.CONTEXT] += 1
                indicators[ResearchClass.CONTEXT].append(kw)
        
        # Artifact indicators
        artifact_keywords = ['letter', 'postcard', 'dear', 'sincerely', 
                           'program', 'ticket', 'stub', 'photograph',
                           'circus presents', 'dated']
        for kw in artifact_keywords:
            if kw in content_lower or kw in filename_lower:
                scores[ResearchClass.ARTIFACT] += 1
                indicators[ResearchClass.ARTIFACT].append(kw)
        
        # Craft indicators
        craft_keywords = ['style', 'writing', 'prose', 'voice', 'hemingway',
                         'steinbeck', 'fitzgerald', 'technique', 'craft',
                         'workflow', 'process', 'draft', 'revision']
        for kw in craft_keywords:
            if kw in content_lower or kw in filename_lower:
                scores[ResearchClass.CRAFT] += 1
                indicators[ResearchClass.CRAFT].append(kw)
        
        # Find highest score
        max_class = max(scores, key=scores.get)
        max_score = scores[max_class]
        
        # Find second highest
        sorted_classes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        alt_class = sorted_classes[1][0] if sorted_classes[1][1] > 0 else None
        
        # Confidence based on margin
        total = sum(scores.values()) or 1
        confidence = max_score / total if total > 0 else 0.5
        
        # Default to context if nothing matched
        if max_score == 0:
            max_class = ResearchClass.CONTEXT
            confidence = 0.3
        
        return ClassificationResult(
            primary_class=max_class,
            confidence=min(confidence, 0.95),
            subtype=None,  # Keyword analysis doesn't determine subtype
            reasoning=f"Keyword analysis found {max_score} indicators",
            alternative_class=alt_class,
            key_indicators=indicators[max_class][:5]
        )
    
    def classify(self, filepath: Path) -> ClassificationResult:
        """
        Classify a document into one of the four research classes.
        
        Uses AI if available, falls back to keyword analysis.
        """
        filepath = Path(filepath)
        content = self._read_document(filepath)
        
        # Truncate for prompt
        content_preview = content[:3000]
        if len(content) > 3000:
            content_preview += "\n\n[... truncated ...]"
        
        # Try AI classification
        if self.model_client:
            prompt = self.CLASSIFICATION_PROMPT.format(
                filename=filepath.name,
                content_preview=content_preview
            )
            
            try:
                response = self.model_client.generate(prompt)
                
                # Parse JSON from response
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    data = json.loads(json_match.group())
                    
                    primary = ResearchClass(data.get("primary_class", "context"))
                    alt = None
                    if data.get("alternative_class"):
                        try:
                            alt = ResearchClass(data["alternative_class"])
                        except ValueError:
                            pass
                    
                    return ClassificationResult(
                        primary_class=primary,
                        confidence=float(data.get("confidence", 0.8)),
                        subtype=data.get("subtype"),
                        reasoning=data.get("reasoning", "AI classification"),
                        alternative_class=alt,
                        key_indicators=data.get("key_indicators", [])
                    )
            except Exception as e:
                # Fall through to keyword analysis
                pass
        
        # Fallback to keyword analysis
        return self._keyword_based_classification(content, filepath.name)
    
    def suggest_subtype(
        self, 
        research_class: ResearchClass, 
        content: str,
        filename: str
    ) -> Optional[str]:
        """Suggest a subtype within a class."""
        subtypes = self.SUBTYPES.get(research_class, [])
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        for subtype in subtypes:
            if subtype in content_lower or subtype in filename_lower:
                return subtype
        
        return subtypes[0] if subtypes else None
    
    def batch_classify(self, filepaths: List[Path]) -> Dict[str, ClassificationResult]:
        """Classify multiple documents."""
        results = {}
        for fp in filepaths:
            try:
                results[str(fp)] = self.classify(fp)
            except Exception as e:
                results[str(fp)] = ClassificationResult(
                    primary_class=ResearchClass.CONTEXT,
                    confidence=0.0,
                    subtype=None,
                    reasoning=f"Error: {e}",
                    alternative_class=None,
                    key_indicators=[]
                )
        return results


# Convenience functions

def classify_document(filepath: str, base_dir: str = ".", model_client=None) -> Dict:
    """Classify a single document."""
    classifier = ResearchClassifier(Path(base_dir), model_client)
    result = classifier.classify(Path(filepath))
    
    return {
        "primary_class": result.primary_class.value,
        "confidence": result.confidence,
        "subtype": result.subtype,
        "reasoning": result.reasoning,
        "alternative_class": result.alternative_class.value if result.alternative_class else None,
        "key_indicators": result.key_indicators
    }


def get_subtypes(research_class: str) -> List[str]:
    """Get available subtypes for a research class."""
    try:
        rc = ResearchClass(research_class)
        return ResearchClassifier.SUBTYPES.get(rc, [])
    except ValueError:
        return []
