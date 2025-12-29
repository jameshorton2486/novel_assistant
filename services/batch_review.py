"""
Batch Review Service - Process multiple chapters with AI review.
Supports parallel processing, progress tracking, and result aggregation.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.base_model import BaseModel, ModelResponse
from models.model_router import get_router
from services.reference_loader import (
    ReferenceLoader, 
    ReferenceBundle, 
    ChapterMetadata,
    extract_metadata_from_chapter
)


class ReviewType(Enum):
    """Types of reviews available."""
    CONSISTENCY = "consistency"
    PROSE = "prose"
    HISTORICAL = "historical"
    FULL = "full"


class ReviewStatus(Enum):
    """Status of a chapter review."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChapterReviewResult:
    """Result of reviewing a single chapter."""
    chapter_number: int
    chapter_title: str
    status: ReviewStatus
    review_type: str
    review_text: str = ""
    model_used: str = ""
    tokens_used: int = 0
    cost_estimate: float = 0.0
    timestamp: str = ""
    error_message: Optional[str] = None
    issues_found: List[str] = field(default_factory=list)


@dataclass
class BatchReviewResult:
    """Result of a full batch review."""
    total_chapters: int
    completed: int
    failed: int
    skipped: int
    total_tokens: int
    total_cost: float
    review_type: str
    model_used: str
    timestamp: str
    chapter_results: List[ChapterReviewResult] = field(default_factory=list)
    summary: str = ""
    critical_issues: List[str] = field(default_factory=list)


class BatchReviewService:
    """
    Service for batch reviewing multiple chapters.
    Handles chapter loading, reference management, and result aggregation.
    """
    
    def __init__(
        self,
        chapters_dir: str = "chapters",
        research_dir: str = "research",
        reviews_dir: str = "reviews",
        reference_dir: str = "reference"
    ):
        """
        Initialize the batch review service.
        
        Args:
            chapters_dir: Directory containing chapter files
            research_dir: Directory containing research documents
            reviews_dir: Directory to save review results
            reference_dir: Directory containing reference files
        """
        self.chapters_dir = Path(chapters_dir)
        self.research_dir = Path(research_dir)
        self.reviews_dir = Path(reviews_dir)
        self.reference_dir = Path(reference_dir)
        
        self.reference_loader = ReferenceLoader(str(reference_dir))
        self.router = get_router()
        
        # Ensure directories exist
        for d in [self.chapters_dir, self.research_dir, self.reviews_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Progress tracking
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
        self._cancel_flag = threading.Event()
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """
        Set a callback for progress updates.
        
        Args:
            callback: Function taking (current, total, message)
        """
        self._progress_callback = callback
    
    def _report_progress(self, current: int, total: int, message: str):
        """Report progress through callback if set."""
        if self._progress_callback:
            self._progress_callback(current, total, message)
    
    def cancel(self):
        """Cancel an ongoing batch review."""
        self._cancel_flag.set()
    
    def list_chapters(self) -> List[Dict[str, Any]]:
        """
        List all chapters in the chapters directory.
        
        Returns:
            List of chapter info dicts with filename, number, title
        """
        chapters = []
        extensions = (".md", ".txt", ".docx")
        
        for f in sorted(self.chapters_dir.iterdir()):
            if f.suffix.lower() in extensions:
                # Try to extract chapter number from filename
                name = f.stem
                number = 0
                title = name
                
                # Common patterns: "chapter_1", "ch1", "01_title"
                for pattern in ["chapter_", "ch", "chapter"]:
                    if name.lower().startswith(pattern):
                        rest = name[len(pattern):]
                        parts = rest.split("_", 1)
                        try:
                            number = int(parts[0])
                            title = parts[1] if len(parts) > 1 else ""
                        except ValueError:
                            pass
                        break
                
                # Try numeric prefix
                if number == 0:
                    parts = name.split("_", 1)
                    try:
                        number = int(parts[0])
                        title = parts[1] if len(parts) > 1 else ""
                    except ValueError:
                        pass
                
                chapters.append({
                    "filename": f.name,
                    "path": str(f),
                    "number": number,
                    "title": title.replace("_", " ").title(),
                    "size": f.stat().st_size
                })
        
        # Sort by chapter number
        chapters.sort(key=lambda x: (x["number"], x["filename"]))
        return chapters
    
    def load_chapter(self, filename: str) -> Optional[str]:
        """
        Load a chapter's content.
        
        Args:
            filename: Chapter filename
            
        Returns:
            Chapter text or None if not found
        """
        path = self.chapters_dir / filename
        
        if not path.exists():
            return None
        
        if path.suffix.lower() == ".docx":
            # Use python-docx for Word files
            try:
                from docx import Document
                doc = Document(str(path))
                return "\n\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                return None
            except Exception:
                return None
        else:
            # Plain text or markdown
            return path.read_text(encoding="utf-8")
    
    def save_chapter(self, filename: str, content: str) -> bool:
        """
        Save chapter content to file.
        
        Args:
            filename: Chapter filename
            content: Chapter content
            
        Returns:
            True if successful
        """
        path = self.chapters_dir / filename
        try:
            path.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False
    
    def list_research(self) -> List[Dict[str, Any]]:
        """
        List all research documents.
        
        Returns:
            List of research file info dicts
        """
        research = []
        extensions = (".md", ".txt", ".docx", ".pdf")
        
        # Walk through research directory including subdirectories
        for root, dirs, files in os.walk(self.research_dir):
            rel_root = Path(root).relative_to(self.research_dir)
            category = str(rel_root) if str(rel_root) != "." else "general"
            
            for f in files:
                if Path(f).suffix.lower() in extensions:
                    full_path = Path(root) / f
                    research.append({
                        "filename": f,
                        "path": str(full_path),
                        "category": category,
                        "size": full_path.stat().st_size
                    })
        
        return research
    
    def review_single_chapter(
        self,
        chapter_info: Dict[str, Any],
        review_type: ReviewType = ReviewType.FULL,
        model_key: Optional[str] = None
    ) -> ChapterReviewResult:
        """
        Review a single chapter.
        
        Args:
            chapter_info: Chapter info dict from list_chapters()
            review_type: Type of review to perform
            model_key: Model to use (defaults to current)
            
        Returns:
            ChapterReviewResult with review feedback
        """
        result = ChapterReviewResult(
            chapter_number=chapter_info.get("number", 0),
            chapter_title=chapter_info.get("title", ""),
            status=ReviewStatus.IN_PROGRESS,
            review_type=review_type.value,
            timestamp=datetime.now().isoformat()
        )
        
        # Load chapter content
        content = self.load_chapter(chapter_info["filename"])
        if not content:
            result.status = ReviewStatus.FAILED
            result.error_message = f"Could not load chapter: {chapter_info['filename']}"
            return result
        
        # Get metadata and load appropriate references
        metadata = extract_metadata_from_chapter(content, chapter_info.get("number", 0))
        
        # If no metadata, load full bundle (less token-efficient but works)
        if not metadata.characters and not metadata.locations:
            bundle = self.reference_loader.load_full_bundle()
        else:
            bundle = self.reference_loader.load_bundle_for_chapter(metadata)
        
        reference_context = bundle.get_combined_context()
        
        # Get model
        model = self.router.get_model(model_key) if model_key else self.router.get_current_model()
        if not model or not model.is_available():
            result.status = ReviewStatus.FAILED
            result.error_message = "AI model not available"
            return result
        
        result.model_used = model.model_id
        
        # Perform review
        response = model.review_chapter(
            chapter_text=content,
            reference_context=reference_context,
            review_type=review_type.value
        )
        
        if response.success:
            result.status = ReviewStatus.COMPLETED
            result.review_text = response.text
            result.tokens_used = response.tokens_used
            result.cost_estimate = response.cost_estimate
            
            # Extract issues (simple heuristic: lines starting with - or *)
            for line in response.text.split("\n"):
                line = line.strip()
                if line.startswith(("-", "*", "•")) and len(line) > 3:
                    result.issues_found.append(line[1:].strip())
        else:
            result.status = ReviewStatus.FAILED
            result.error_message = response.error_message
        
        return result
    
    def run_batch_review(
        self,
        chapter_numbers: Optional[List[int]] = None,
        review_type: ReviewType = ReviewType.FULL,
        model_key: Optional[str] = None,
        parallel: bool = False
    ) -> BatchReviewResult:
        """
        Run a batch review across multiple chapters.
        
        Args:
            chapter_numbers: Specific chapters to review (None = all)
            review_type: Type of review to perform
            model_key: Model to use
            parallel: Whether to run reviews in parallel
            
        Returns:
            BatchReviewResult with aggregated results
        """
        self._cancel_flag.clear()
        
        chapters = self.list_chapters()
        
        # Filter to requested chapters
        if chapter_numbers:
            chapters = [c for c in chapters if c["number"] in chapter_numbers]
        
        result = BatchReviewResult(
            total_chapters=len(chapters),
            completed=0,
            failed=0,
            skipped=0,
            total_tokens=0,
            total_cost=0.0,
            review_type=review_type.value,
            model_used=model_key or self.router._current_model_key,
            timestamp=datetime.now().isoformat()
        )
        
        if not chapters:
            result.summary = "No chapters found to review."
            return result
        
        self._report_progress(0, len(chapters), "Starting batch review...")
        
        # Sequential processing (parallel can hit rate limits)
        for i, chapter in enumerate(chapters):
            if self._cancel_flag.is_set():
                result.skipped = len(chapters) - i
                break
            
            self._report_progress(i, len(chapters), f"Reviewing Chapter {chapter['number']}...")
            
            chapter_result = self.review_single_chapter(
                chapter_info=chapter,
                review_type=review_type,
                model_key=model_key
            )
            
            result.chapter_results.append(chapter_result)
            
            if chapter_result.status == ReviewStatus.COMPLETED:
                result.completed += 1
                result.total_tokens += chapter_result.tokens_used
                result.total_cost += chapter_result.cost_estimate
            elif chapter_result.status == ReviewStatus.FAILED:
                result.failed += 1
        
        self._report_progress(len(chapters), len(chapters), "Review complete!")
        
        # Generate summary
        result.summary = self._generate_summary(result)
        result.critical_issues = self._extract_critical_issues(result)
        
        # Save results
        self._save_batch_result(result)
        
        return result
    
    def _generate_summary(self, result: BatchReviewResult) -> str:
        """Generate a human-readable summary of the batch review."""
        lines = [
            f"## Batch Review Summary",
            f"",
            f"**Review Type:** {result.review_type}",
            f"**Model:** {result.model_used}",
            f"**Chapters Reviewed:** {result.completed}/{result.total_chapters}",
            f"**Failed:** {result.failed}",
            f"**Total Tokens:** {result.total_tokens:,}",
            f"**Estimated Cost:** ${result.total_cost:.4f}",
            f""
        ]
        
        # Per-chapter summary
        if result.chapter_results:
            lines.append("### Chapter Results")
            for cr in result.chapter_results:
                status_icon = "✓" if cr.status == ReviewStatus.COMPLETED else "✗"
                issues = len(cr.issues_found)
                lines.append(f"- {status_icon} Chapter {cr.chapter_number}: {issues} issues found")
        
        return "\n".join(lines)
    
    def _extract_critical_issues(self, result: BatchReviewResult) -> List[str]:
        """Extract critical/high-priority issues from all chapters."""
        critical = []
        keywords = ["critical", "error", "incorrect", "wrong", "anachronism", "inconsistent"]
        
        for cr in result.chapter_results:
            for issue in cr.issues_found:
                if any(kw in issue.lower() for kw in keywords):
                    critical.append(f"Ch{cr.chapter_number}: {issue}")
        
        return critical
    
    def _save_batch_result(self, result: BatchReviewResult):
        """Save batch review results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_review_{result.review_type}_{timestamp}.json"
        path = self.reviews_dir / filename
        
        # Convert to serializable dict
        data = {
            "total_chapters": result.total_chapters,
            "completed": result.completed,
            "failed": result.failed,
            "skipped": result.skipped,
            "total_tokens": result.total_tokens,
            "total_cost": result.total_cost,
            "review_type": result.review_type,
            "model_used": result.model_used,
            "timestamp": result.timestamp,
            "summary": result.summary,
            "critical_issues": result.critical_issues,
            "chapter_results": [
                {
                    "chapter_number": cr.chapter_number,
                    "chapter_title": cr.chapter_title,
                    "status": cr.status.value,
                    "review_type": cr.review_type,
                    "review_text": cr.review_text,
                    "model_used": cr.model_used,
                    "tokens_used": cr.tokens_used,
                    "cost_estimate": cr.cost_estimate,
                    "issues_found": cr.issues_found,
                    "error_message": cr.error_message
                }
                for cr in result.chapter_results
            ]
        }
        
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        
        # Also save markdown summary
        md_path = self.reviews_dir / f"batch_review_{result.review_type}_{timestamp}.md"
        md_path.write_text(result.summary, encoding="utf-8")
    
    def save_chapter_review(self, result: ChapterReviewResult):
        """Save a single chapter review result."""
        filename = f"review_ch{result.chapter_number}_{result.review_type}.md"
        path = self.reviews_dir / filename
        
        content = f"""# Chapter {result.chapter_number} Review
**Title:** {result.chapter_title}
**Review Type:** {result.review_type}
**Model:** {result.model_used}
**Timestamp:** {result.timestamp}
**Tokens Used:** {result.tokens_used}
**Cost:** ${result.cost_estimate:.4f}

---

{result.review_text}
"""
        path.write_text(content, encoding="utf-8")
