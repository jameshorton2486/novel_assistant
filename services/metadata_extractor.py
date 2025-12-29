"""
Chapter Metadata Extractor
==========================

PHASE 2 FEATURE

Extracts structured metadata from chapters:
- POV character
- Location(s)
- Timeline (date/time)
- Characters present
- Artifacts mentioned
- Key events
- Word count
- Scene count

Output: chapters/metadata/chapter_XX_meta.json
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ChapterMetadata:
    """Extracted metadata for a chapter."""
    chapter_num: int
    title: str
    pov: str
    locations: List[str]
    timeline: str
    characters: List[str]
    artifacts: List[str]
    key_events: List[str]
    word_count: int
    scene_count: int
    extracted_at: str


class MetadataExtractor:
    """
    Extracts metadata from chapters for tracking and consistency.
    
    Uses:
    - Pattern matching for locations, characters
    - AI assistance for events and POV
    - Canon reference for validation
    """
    
    # Known characters for matching
    KNOWN_CHARACTERS = [
        "Tommy", "Jenny", "Rafael", "Vic", "Silas", "Eddie",
        "Marcus", "Frank", "Margaret", "Carl", "Carlos", "Sarah"
    ]
    
    # Known locations
    KNOWN_LOCATIONS = [
        "Sacramento", "Stockton", "Fresno", "Modesto", "Bakersfield",
        "big top", "back yard", "cookhouse", "bandstand", "rail yard",
        "Glendale", "Phoenix", "San Antonio"
    ]
    
    def __init__(self, base_dir: Path, model_client=None):
        self.base_dir = Path(base_dir)
        self.chapters_dir = self.base_dir / "chapters"
        self.metadata_dir = self.chapters_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        self.model_client = model_client
    
    def _read_chapter(self, chapter_num: int) -> Optional[str]:
        """Read chapter content."""
        for ext in ['.md', '.docx']:
            path = self.chapters_dir / f"chapter_{chapter_num:02d}{ext}"
            if path.exists():
                if ext == '.md':
                    return path.read_text(encoding='utf-8')
                else:
                    try:
                        from docx import Document
                        doc = Document(path)
                        return '\n\n'.join([p.text for p in doc.paragraphs])
                    except ImportError:
                        return None
        return None
    
    def _extract_title(self, text: str, chapter_num: int) -> str:
        """Extract chapter title."""
        match = re.search(r'^#?\s*Chapter\s*\d+[:.]\s*(.+)$', text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return f"Chapter {chapter_num}"
    
    def _count_scenes(self, text: str) -> int:
        """Count scene breaks."""
        # Scene breaks are typically *** or ---
        breaks = len(re.findall(r'\n\s*[*#-]{3,}\s*\n', text))
        return breaks + 1  # Number of scenes = breaks + 1
    
    def _find_characters(self, text: str) -> List[str]:
        """Find mentioned characters."""
        found = []
        text_lower = text.lower()
        for char in self.KNOWN_CHARACTERS:
            if char.lower() in text_lower:
                found.append(char)
        return found
    
    def _find_locations(self, text: str) -> List[str]:
        """Find mentioned locations."""
        found = []
        text_lower = text.lower()
        for loc in self.KNOWN_LOCATIONS:
            if loc.lower() in text_lower:
                found.append(loc)
        return found
    
    def _extract_with_ai(self, text: str, chapter_num: int) -> Dict:
        """Use AI to extract complex metadata."""
        if not self.model_client:
            return {
                "pov": "Tommy",  # Default
                "timeline": "Unknown",
                "key_events": [],
                "artifacts": []
            }
        
        prompt = f"""Analyze this chapter and extract metadata.

CHAPTER TEXT (excerpt):
{text[:5000]}

Return JSON only:
{{
    "pov": "primary POV character name",
    "timeline": "when this takes place (e.g., 'Early May 1954, morning')",
    "key_events": ["event 1", "event 2", "event 3"],
    "artifacts": ["any physical objects that are significant"]
}}
"""
        try:
            response = self.model_client.generate(prompt)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        return {
            "pov": "Tommy",
            "timeline": "Unknown",
            "key_events": [],
            "artifacts": []
        }
    
    def extract(self, chapter_num: int) -> Optional[ChapterMetadata]:
        """Extract metadata from a chapter."""
        text = self._read_chapter(chapter_num)
        if not text:
            return None
        
        # Basic extraction
        title = self._extract_title(text, chapter_num)
        word_count = len(text.split())
        scene_count = self._count_scenes(text)
        characters = self._find_characters(text)
        locations = self._find_locations(text)
        
        # AI extraction for complex fields
        ai_data = self._extract_with_ai(text, chapter_num)
        
        metadata = ChapterMetadata(
            chapter_num=chapter_num,
            title=title,
            pov=ai_data.get("pov", "Tommy"),
            locations=locations,
            timeline=ai_data.get("timeline", "Unknown"),
            characters=characters,
            artifacts=ai_data.get("artifacts", []),
            key_events=ai_data.get("key_events", []),
            word_count=word_count,
            scene_count=scene_count,
            extracted_at=datetime.now().isoformat()
        )
        
        # Save
        self._save_metadata(metadata)
        
        return metadata
    
    def _save_metadata(self, metadata: ChapterMetadata):
        """Save metadata to JSON file."""
        filepath = self.metadata_dir / f"chapter_{metadata.chapter_num:02d}_meta.json"
        filepath.write_text(json.dumps(asdict(metadata), indent=2))
    
    def extract_all(self) -> List[ChapterMetadata]:
        """Extract metadata from all chapters."""
        results = []
        for i in range(1, 13):
            meta = self.extract(i)
            if meta:
                results.append(meta)
        return results
    
    def get_metadata(self, chapter_num: int) -> Optional[Dict]:
        """Get previously extracted metadata."""
        filepath = self.metadata_dir / f"chapter_{chapter_num:02d}_meta.json"
        if filepath.exists():
            return json.loads(filepath.read_text())
        return None
    
    def get_character_appearances(self, character: str) -> List[int]:
        """Get chapters where a character appears."""
        appearances = []
        for i in range(1, 13):
            meta = self.get_metadata(i)
            if meta and character in meta.get("characters", []):
                appearances.append(i)
        return appearances
    
    def get_timeline_summary(self) -> List[Dict]:
        """Get timeline across all chapters."""
        timeline = []
        for i in range(1, 13):
            meta = self.get_metadata(i)
            if meta:
                timeline.append({
                    "chapter": i,
                    "title": meta.get("title"),
                    "timeline": meta.get("timeline"),
                    "locations": meta.get("locations", [])
                })
        return timeline


# Convenience functions

def extract_chapter_metadata(chapter_num: int, base_dir: str = ".", model_client=None) -> Dict:
    """Extract metadata from a single chapter."""
    extractor = MetadataExtractor(Path(base_dir), model_client)
    meta = extractor.extract(chapter_num)
    return asdict(meta) if meta else {"error": "Chapter not found"}


def extract_all_metadata(base_dir: str = ".", model_client=None) -> List[Dict]:
    """Extract metadata from all chapters."""
    extractor = MetadataExtractor(Path(base_dir), model_client)
    results = extractor.extract_all()
    return [asdict(m) for m in results]


def get_timeline(base_dir: str = ".") -> List[Dict]:
    """Get timeline summary."""
    extractor = MetadataExtractor(Path(base_dir))
    return extractor.get_timeline_summary()
