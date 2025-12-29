"""
Canon Manager - Tracks versioning, locking, and fact governance.

PROMOTION RULE: A fact enters CANON only when it appears on the page.
Research digests never override canon.
"""

import json
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


class ChapterState(Enum):
    """Chapter lock states."""
    DRAFT = "draft"               # Initial writing, free editing
    REVISED = "revised"           # After first revision pass
    CANON_LOCKED = "canon_locked" # Requires explicit unlock + reason
    PUBLISHED = "published"       # Final version, read-only


@dataclass
class CanonFact:
    """A single canon fact."""
    key: str
    value: str
    source_chapter: str
    created: str
    updated: str
    history: List[Dict]


@dataclass
class ChapterRecord:
    """Chapter state tracking."""
    name: str
    state: str
    last_modified: str
    lock_reason: Optional[str] = None
    unlock_history: List[Dict] = None
    
    def __post_init__(self):
        if self.unlock_history is None:
            self.unlock_history = []


class CanonManager:
    """
    Manages canon versioning and chapter locking.
    
    Usage:
        canon = CanonManager("/path/to/novel_assistant")
        
        # Add a fact
        canon.add_fact("tommy_age", "19", "Chapter 1")
        
        # Lock a chapter
        canon.set_chapter_state("Chapter 5", ChapterState.CANON_LOCKED)
        
        # Validate text against canon
        issues = canon.validate_against_canon(chapter_text)
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.reference_path = self.base_path / "reference"
        self.version_file = self.reference_path / "canon_version.json"
        self.changelog_file = self.reference_path / "canon_changelog.md"
        self.chapters_state_file = self.reference_path / "chapter_states.json"
        
        # Ensure reference directory exists
        self.reference_path.mkdir(parents=True, exist_ok=True)
        
        self._load_data()
    
    def _load_data(self):
        """Load canon version and chapter states."""
        # Load canon version
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                self.canon = json.load(f)
        else:
            self.canon = self._create_default_canon()
            self._save_canon()
        
        # Load chapter states
        if self.chapters_state_file.exists():
            with open(self.chapters_state_file, 'r', encoding='utf-8') as f:
                self.chapter_states = json.load(f)
        else:
            self.chapter_states = {}
            self._save_chapter_states()
    
    def _create_default_canon(self) -> Dict:
        """Create default canon structure."""
        return {
            "version": "1.0.0",
            "last_update": datetime.now().isoformat(),
            "novel": {
                "title": "Untitled",
                "setting_period": "May-June 1954",
                "setting_location": "California circus circuit"
            },
            "characters": {},
            "timeline": {},
            "locations": {},
            "objects": {},
            "facts": {}
        }
    
    def _save_canon(self):
        """Save canon to file."""
        self.canon["last_update"] = datetime.now().isoformat()
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(self.canon, f, indent=2)
    
    def _save_chapter_states(self):
        """Save chapter states to file."""
        with open(self.chapters_state_file, 'w', encoding='utf-8') as f:
            json.dump(self.chapter_states, f, indent=2)
    
    def _log_changelog(self, action: str, details: str, affected_chapters: List[str] = None):
        """Append to changelog."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"\n## {timestamp}\n\n"
        entry += f"**Action:** {action}\n\n"
        entry += f"**Details:** {details}\n\n"
        
        if affected_chapters:
            entry += f"**Affected Chapters:** {', '.join(affected_chapters)}\n\n"
        
        entry += "---\n"
        
        with open(self.changelog_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def _bump_version(self, bump_type: str = "patch"):
        """Increment version number."""
        parts = self.canon["version"].split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1
        
        self.canon["version"] = f"{major}.{minor}.{patch}"
    
    # -------------------------------------------------
    # FACT MANAGEMENT
    # -------------------------------------------------
    
    def add_fact(self, fact_key: str, fact_value: str, source_chapter: str,
                 category: str = "facts") -> Dict:
        """
        Add new canon fact (requires page source).
        
        Args:
            fact_key: Unique identifier for the fact
            fact_value: The factual value
            source_chapter: Chapter where this fact appears
            category: One of characters, timeline, locations, objects, facts
            
        Returns:
            The created fact record
        """
        if category not in self.canon:
            self.canon[category] = {}
        
        now = datetime.now().isoformat()
        
        fact = {
            "value": fact_value,
            "source_chapter": source_chapter,
            "created": now,
            "updated": now,
            "history": []
        }
        
        self.canon[category][fact_key] = fact
        self._bump_version()
        self._save_canon()
        self._log_changelog(
            "ADD_FACT",
            f"Added {category}/{fact_key}: {fact_value}",
            [source_chapter]
        )
        
        return fact
    
    def update_fact(self, fact_key: str, new_value: str, reason: str,
                    affected_chapters: List[str], category: str = "facts") -> Dict:
        """
        Update existing canon fact with changelog entry.
        
        Args:
            fact_key: Fact to update
            new_value: New value
            reason: Why this is being changed
            affected_chapters: Chapters that reference this fact
            category: Category of the fact
            
        Returns:
            Updated fact record
        """
        if category not in self.canon or fact_key not in self.canon[category]:
            raise KeyError(f"Fact not found: {category}/{fact_key}")
        
        fact = self.canon[category][fact_key]
        old_value = fact["value"]
        
        # Add to history
        fact["history"].append({
            "old_value": old_value,
            "changed": datetime.now().isoformat(),
            "reason": reason
        })
        
        fact["value"] = new_value
        fact["updated"] = datetime.now().isoformat()
        
        self._bump_version("minor")
        self._save_canon()
        self._log_changelog(
            "UPDATE_FACT",
            f"Changed {category}/{fact_key}: '{old_value}' → '{new_value}'\nReason: {reason}",
            affected_chapters
        )
        
        return fact
    
    def get_fact(self, fact_key: str, category: str = "facts") -> Optional[Dict]:
        """Get a canon fact by key."""
        if category in self.canon and fact_key in self.canon[category]:
            return self.canon[category][fact_key]
        return None
    
    def get_all_facts(self, category: str = None) -> Dict:
        """Get all facts, optionally filtered by category."""
        if category:
            return self.canon.get(category, {})
        
        all_facts = {}
        for cat in ["characters", "timeline", "locations", "objects", "facts"]:
            all_facts[cat] = self.canon.get(cat, {})
        return all_facts
    
    # -------------------------------------------------
    # CHAPTER STATE MANAGEMENT
    # -------------------------------------------------
    
    def get_chapter_state(self, chapter_name: str) -> ChapterState:
        """Get current lock state of chapter."""
        if chapter_name in self.chapter_states:
            state_str = self.chapter_states[chapter_name].get("state", "draft")
            return ChapterState(state_str)
        return ChapterState.DRAFT
    
    def set_chapter_state(self, chapter_name: str, state: ChapterState,
                          reason: str = None) -> Dict:
        """
        Set chapter lock state.
        
        Args:
            chapter_name: Name of the chapter
            state: New state
            reason: Required for unlocking CANON_LOCKED or PUBLISHED
            
        Returns:
            Updated chapter record
        """
        now = datetime.now().isoformat()
        
        # Get or create chapter record
        if chapter_name not in self.chapter_states:
            self.chapter_states[chapter_name] = {
                "name": chapter_name,
                "state": ChapterState.DRAFT.value,
                "last_modified": now,
                "lock_reason": None,
                "unlock_history": []
            }
        
        record = self.chapter_states[chapter_name]
        old_state = record["state"]
        
        # Check if unlocking requires reason
        if old_state in [ChapterState.CANON_LOCKED.value, ChapterState.PUBLISHED.value]:
            if state in [ChapterState.DRAFT, ChapterState.REVISED]:
                if not reason:
                    raise ValueError(f"Reason required to unlock from {old_state}")
                
                record["unlock_history"].append({
                    "from_state": old_state,
                    "to_state": state.value,
                    "reason": reason,
                    "timestamp": now
                })
        
        record["state"] = state.value
        record["last_modified"] = now
        
        if state in [ChapterState.CANON_LOCKED, ChapterState.PUBLISHED]:
            record["lock_reason"] = reason
        
        self._save_chapter_states()
        self._log_changelog(
            "CHAPTER_STATE_CHANGE",
            f"{chapter_name}: {old_state} → {state.value}" + 
            (f"\nReason: {reason}" if reason else ""),
            [chapter_name]
        )
        
        return record
    
    def get_all_chapter_states(self) -> Dict[str, ChapterState]:
        """Get states for all tracked chapters."""
        return {
            name: ChapterState(data["state"])
            for name, data in self.chapter_states.items()
        }
    
    def is_editable(self, chapter_name: str) -> bool:
        """Check if chapter can be edited."""
        state = self.get_chapter_state(chapter_name)
        return state in [ChapterState.DRAFT, ChapterState.REVISED]
    
    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------
    
    def validate_against_canon(self, chapter_text: str) -> List[Dict]:
        """
        Check chapter text against canon facts.
        
        Args:
            chapter_text: The chapter content to validate
            
        Returns:
            List of potential inconsistencies (flags only, no auto-fix)
        """
        issues = []
        text_lower = chapter_text.lower()
        
        # Check all categories
        for category in ["characters", "timeline", "locations", "objects", "facts"]:
            facts = self.canon.get(category, {})
            
            for fact_key, fact_data in facts.items():
                value = fact_data["value"]
                
                # Simple check: if fact key mentioned but value different
                if fact_key.lower().replace("_", " ") in text_lower:
                    # This is a basic check - could be enhanced with NLP
                    if value.lower() not in text_lower:
                        issues.append({
                            "type": "potential_inconsistency",
                            "category": category,
                            "fact_key": fact_key,
                            "canon_value": value,
                            "severity": "warning",
                            "message": f"Canon fact '{fact_key}' referenced but value '{value}' not found"
                        })
        
        return issues
    
    def get_canon_summary(self) -> str:
        """Get a formatted summary of all canon facts."""
        lines = [
            f"# Canon Summary v{self.canon['version']}",
            f"Last Updated: {self.canon['last_update']}",
            "",
            f"## Novel: {self.canon['novel']['title']}",
            f"- Setting: {self.canon['novel']['setting_period']}",
            f"- Location: {self.canon['novel']['setting_location']}",
            ""
        ]
        
        for category in ["characters", "timeline", "locations", "objects", "facts"]:
            facts = self.canon.get(category, {})
            if facts:
                lines.append(f"## {category.title()}")
                for key, data in facts.items():
                    lines.append(f"- **{key}**: {data['value']} (from {data['source_chapter']})")
                lines.append("")
        
        return "\n".join(lines)
