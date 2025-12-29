"""
Chapter Locking System
======================

Manages chapter states to protect finalized content.

States:
- DRAFT: Free editing
- REVISED: After first revision pass
- CANON_LOCKED: Requires explicit unlock + reason
- PUBLISHED: Final version, read-only
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ChapterState(Enum):
    """Chapter lock states."""
    DRAFT = "draft"                 # Free editing
    REVISED = "revised"             # After revision pass
    CANON_LOCKED = "canon_locked"   # Protected, unlock required
    PUBLISHED = "published"         # Final, read-only


@dataclass
class ChapterLock:
    """Lock status for a chapter."""
    chapter_num: int
    state: str
    locked_at: Optional[str]
    locked_by: Optional[str]
    lock_reason: Optional[str]
    last_modified: str
    word_count: int
    revision_count: int


@dataclass
class UnlockRequest:
    """Request to unlock a protected chapter."""
    chapter_num: int
    requested_at: str
    requested_by: str
    reason: str
    approved: bool = False
    approved_at: Optional[str] = None


class ChapterLocker:
    """
    Manages chapter protection states.
    
    Rules:
    - DRAFT → REVISED: Allowed freely
    - REVISED → CANON_LOCKED: Requires confirmation
    - CANON_LOCKED → unlock: Requires explicit reason
    - PUBLISHED: Cannot be changed
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.chapters_dir = self.base_dir / "chapters"
        self.locks_file = self.base_dir / "chapter_locks.json"
        
        self.locks: Dict[int, ChapterLock] = {}
        self._load_locks()
    
    def _load_locks(self):
        """Load lock states from disk."""
        if self.locks_file.exists():
            data = json.loads(self.locks_file.read_text())
            self.locks = {
                int(k): ChapterLock(**v) 
                for k, v in data.items()
            }
    
    def _save_locks(self):
        """Save lock states to disk."""
        data = {str(k): asdict(v) for k, v in self.locks.items()}
        self.locks_file.write_text(json.dumps(data, indent=2))
    
    def _get_chapter_info(self, chapter_num: int) -> Dict:
        """Get chapter file info."""
        for ext in ['.md', '.docx']:
            path = self.chapters_dir / f"chapter_{chapter_num:02d}{ext}"
            if path.exists():
                stat = path.stat()
                
                # Word count (rough)
                if ext == '.md':
                    words = len(path.read_text().split())
                else:
                    words = 0  # Would need docx parsing
                
                return {
                    "path": str(path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "words": words
                }
        return {"path": None, "modified": None, "words": 0}
    
    def get_state(self, chapter_num: int) -> ChapterLock:
        """Get current lock state for a chapter."""
        if chapter_num in self.locks:
            return self.locks[chapter_num]
        
        # Default: DRAFT
        info = self._get_chapter_info(chapter_num)
        return ChapterLock(
            chapter_num=chapter_num,
            state=ChapterState.DRAFT.value,
            locked_at=None,
            locked_by=None,
            lock_reason=None,
            last_modified=info.get("modified", datetime.now().isoformat()),
            word_count=info.get("words", 0),
            revision_count=0
        )
    
    def set_state(
        self,
        chapter_num: int,
        new_state: ChapterState,
        reason: str = "",
        by: str = "author"
    ) -> ChapterLock:
        """
        Change chapter state.
        
        Validates state transitions.
        """
        current = self.get_state(chapter_num)
        current_state = ChapterState(current.state)
        
        # Validate transitions
        valid_transitions = {
            ChapterState.DRAFT: [ChapterState.REVISED, ChapterState.CANON_LOCKED],
            ChapterState.REVISED: [ChapterState.DRAFT, ChapterState.CANON_LOCKED, ChapterState.PUBLISHED],
            ChapterState.CANON_LOCKED: [],  # Requires unlock first
            ChapterState.PUBLISHED: [],      # Never changes
        }
        
        if new_state not in valid_transitions.get(current_state, []):
            if current_state == ChapterState.CANON_LOCKED:
                raise ValueError(f"Chapter {chapter_num} is CANON_LOCKED. Use unlock() first.")
            elif current_state == ChapterState.PUBLISHED:
                raise ValueError(f"Chapter {chapter_num} is PUBLISHED. Cannot be changed.")
            else:
                raise ValueError(f"Invalid transition: {current_state.value} → {new_state.value}")
        
        # Update lock
        info = self._get_chapter_info(chapter_num)
        
        lock = ChapterLock(
            chapter_num=chapter_num,
            state=new_state.value,
            locked_at=datetime.now().isoformat() if new_state in [ChapterState.CANON_LOCKED, ChapterState.PUBLISHED] else None,
            locked_by=by if new_state in [ChapterState.CANON_LOCKED, ChapterState.PUBLISHED] else None,
            lock_reason=reason if new_state in [ChapterState.CANON_LOCKED, ChapterState.PUBLISHED] else None,
            last_modified=info.get("modified", datetime.now().isoformat()),
            word_count=info.get("words", 0),
            revision_count=current.revision_count + (1 if new_state == ChapterState.REVISED else 0)
        )
        
        self.locks[chapter_num] = lock
        self._save_locks()
        
        return lock
    
    def unlock(
        self,
        chapter_num: int,
        reason: str,
        by: str = "author"
    ) -> ChapterLock:
        """
        Unlock a CANON_LOCKED chapter.
        
        Requires explicit reason (logged for accountability).
        """
        current = self.get_state(chapter_num)
        
        if current.state != ChapterState.CANON_LOCKED.value:
            raise ValueError(f"Chapter {chapter_num} is not locked (state: {current.state})")
        
        if not reason or len(reason) < 10:
            raise ValueError("Unlock requires a meaningful reason (10+ characters)")
        
        # Log the unlock
        unlock_log = self.base_dir / "unlock_log.json"
        log_entry = {
            "chapter": chapter_num,
            "unlocked_at": datetime.now().isoformat(),
            "unlocked_by": by,
            "reason": reason,
            "previous_lock_date": current.locked_at
        }
        
        if unlock_log.exists():
            logs = json.loads(unlock_log.read_text())
        else:
            logs = []
        logs.append(log_entry)
        unlock_log.write_text(json.dumps(logs, indent=2))
        
        # Set to REVISED (not DRAFT, to preserve revision history)
        return self.set_state(chapter_num, ChapterState.REVISED, f"Unlocked: {reason}", by)
    
    def is_editable(self, chapter_num: int) -> bool:
        """Check if chapter can be edited."""
        state = self.get_state(chapter_num)
        return state.state in [ChapterState.DRAFT.value, ChapterState.REVISED.value]
    
    def get_all_states(self) -> List[Dict]:
        """Get states for all chapters."""
        states = []
        for i in range(1, 13):  # Chapters 1-12
            lock = self.get_state(i)
            states.append({
                "chapter": i,
                "state": lock.state,
                "editable": lock.state in ["draft", "revised"],
                "word_count": lock.word_count,
                "revisions": lock.revision_count
            })
        return states
    
    def lock_for_canon(self, chapter_num: int, reason: str = "Canon finalized") -> ChapterLock:
        """Convenience: Lock chapter as CANON_LOCKED."""
        return self.set_state(chapter_num, ChapterState.CANON_LOCKED, reason)
    
    def mark_revised(self, chapter_num: int) -> ChapterLock:
        """Convenience: Mark chapter as REVISED."""
        return self.set_state(chapter_num, ChapterState.REVISED)


# Convenience functions

def get_chapter_state(chapter_num: int, base_dir: str = ".") -> Dict:
    """Get chapter lock state."""
    locker = ChapterLocker(Path(base_dir))
    return asdict(locker.get_state(chapter_num))


def lock_chapter(chapter_num: int, reason: str = "Canon finalized", base_dir: str = ".") -> Dict:
    """Lock chapter as CANON_LOCKED."""
    locker = ChapterLocker(Path(base_dir))
    return asdict(locker.lock_for_canon(chapter_num, reason))


def unlock_chapter(chapter_num: int, reason: str, base_dir: str = ".") -> Dict:
    """Unlock a locked chapter."""
    locker = ChapterLocker(Path(base_dir))
    return asdict(locker.unlock(chapter_num, reason))


def get_all_chapter_states(base_dir: str = ".") -> List[Dict]:
    """Get states for all chapters."""
    locker = ChapterLocker(Path(base_dir))
    return locker.get_all_states()
