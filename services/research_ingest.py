"""
Research Ingestion Service (v3.1)
=================================

Implements the four-class research governance model:

1. CANON - Novel-bound, sacred facts (→ /reference/)
2. CONTEXT - Background material, non-authoritative (→ /research/context/)
3. ARTIFACT - Trigger material, scene devices (→ /research/artifacts/)
4. CRAFT - Meta-guidance about writing (→ /research/craft/)

CRITICAL RULE: AI classifies and distills. AI does not decide what is true.
Human approval required for all promotions.
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum


class ResearchClass(Enum):
    """
    The four research classes with distinct AI behavior rules.
    """
    CANON = "canon"           # Sacred, always loaded, never contradicted
    CONTEXT = "context"       # Background, read-only, never narrated
    ARTIFACT = "artifact"     # Scene triggers, never summarized generically
    CRAFT = "craft"           # Meta-guidance, never in narrative


# Detailed descriptions for each class
RESEARCH_CLASS_INFO = {
    ResearchClass.CANON: {
        "name": "Canon Research",
        "description": "Facts that appear on the page or govern what may appear",
        "examples": [
            "Timeline dates and events",
            "Character ages, injuries, relationships",
            "Locations as depicted in chapters",
            "Historical events explicitly referenced",
            "Rules like 'no modern slang'"
        ],
        "ai_behavior": [
            "Always loaded (or selectively by chapter)",
            "Never contradicted",
            "Never expanded without human approval"
        ],
        "storage": "reference/"
    },
    ResearchClass.CONTEXT: {
        "name": "Contextual Research",
        "description": "Historically accurate material that informs scenes but is not quoted directly",
        "examples": [
            "Operation Wetback background details",
            "Bracero program specifics",
            "Circus logistics not shown directly",
            "Social attitudes, newspapers, moral climate"
        ],
        "ai_behavior": [
            "Read-only reference",
            "Used for plausibility checks",
            "Never directly narrated to reader",
            "Never 'explained' in prose"
        ],
        "storage": "research/context/"
    },
    ResearchClass.ARTIFACT: {
        "name": "Artifact & Source Research",
        "description": "Documents that exist inside the story world or inspire memory",
        "examples": [
            "Letters and postcards",
            "Ticket stubs and programs",
            "Newspaper clippings",
            "Photographs described in narrative"
        ],
        "ai_behavior": [
            "Never summarized generically",
            "Used as scene triggers only",
            "Interpreted through character POV",
            "Meaning derived from contrast, not exposition"
        ],
        "storage": "research/artifacts/"
    },
    ResearchClass.CRAFT: {
        "name": "Craft & Writing Research",
        "description": "Material about HOW to write, not what happened",
        "examples": [
            "Style guides (Hemingway, Steinbeck, Fitzgerald)",
            "Author influence notes",
            "Workflow and process plans",
            "Beat sheets and structure guides"
        ],
        "ai_behavior": [
            "Used only in drafting/revision modes",
            "Never injected into narrative",
            "Never treated as factual research",
            "Editorial scaffolding only"
        ],
        "storage": "research/craft/"
    }
}


@dataclass
class ResearchDocument:
    """Metadata for an ingested research document."""
    id: str
    original_filename: str
    research_class: str          # canon, context, artifact, craft
    subtype: Optional[str]       # e.g., "historical", "location", "letter"
    upload_date: str
    file_hash: str
    status: str                  # "intake", "classified", "distilled", "approved", "rejected"
    raw_path: str
    classification_confidence: Optional[float] = None
    digest_path: Optional[str] = None
    final_path: Optional[str] = None
    notes: str = ""
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    promotion_target: Optional[str] = None  # If promoting to canon, where?
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResearchDocument':
        return cls(**data)


class ResearchIngestService:
    """
    Manages the intake of research documents using the four-class model.
    
    Pipeline:
    1. INGEST - User uploads file
    2. CLASSIFY - AI determines research class
    3. DISTILL - AI extracts relevant content
    4. PROMOTE - Human approves placement
    5. GOVERN - System enforces usage rules
    """
    
    # Storage paths for each class
    CLASS_PATHS = {
        ResearchClass.CANON: "reference",
        ResearchClass.CONTEXT: "research/context",
        ResearchClass.ARTIFACT: "research/artifacts",
        ResearchClass.CRAFT: "research/craft"
    }
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.intake_dir = self.base_dir / "research" / "intake"
        self.rejected_dir = self.base_dir / "research" / "rejected"
        self.registry_path = self.base_dir / "research" / "registry.json"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load registry
        self.registry: Dict[str, ResearchDocument] = {}
        self._load_registry()
    
    def _ensure_directories(self):
        """Create all required directories."""
        directories = [
            self.intake_dir,
            self.rejected_dir,
            self.base_dir / "research" / "context",
            self.base_dir / "research" / "artifacts",
            self.base_dir / "research" / "craft",
            self.base_dir / "research" / "canon_staging",
            self.base_dir / "reference",
            self.base_dir / "reference" / "characters",
            self.base_dir / "reference" / "locations",
        ]
        for d in directories:
            d.mkdir(parents=True, exist_ok=True)
    
    def _load_registry(self):
        """Load document registry from disk."""
        if self.registry_path.exists():
            data = json.loads(self.registry_path.read_text())
            self.registry = {
                k: ResearchDocument.from_dict(v) 
                for k, v in data.items()
            }
    
    def _save_registry(self):
        """Save document registry to disk."""
        data = {k: v.to_dict() for k, v in self.registry.items()}
        self.registry_path.write_text(json.dumps(data, indent=2))
    
    def _compute_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash for deduplication."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]
    
    def _generate_id(self, filename: str) -> str:
        """Generate unique document ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() else "_" for c in filename[:20])
        return f"doc_{safe_name}_{timestamp}"
    
    def ingest(self, source_path: Path, notes: str = "") -> ResearchDocument:
        """
        Step 1: INGEST - Accept a new document into the intake queue.
        
        Document goes to intake/ and awaits classification.
        No assumptions made about class until AI classifies.
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Check for duplicates
        file_hash = self._compute_hash(source_path)
        for doc in self.registry.values():
            if doc.file_hash == file_hash and doc.status != "rejected":
                raise ValueError(f"Duplicate document: {doc.original_filename}")
        
        # Generate ID and copy to intake
        doc_id = self._generate_id(source_path.name)
        dest_filename = f"{doc_id}{source_path.suffix}"
        dest_path = self.intake_dir / dest_filename
        
        shutil.copy2(source_path, dest_path)
        
        # Create metadata (class TBD)
        doc = ResearchDocument(
            id=doc_id,
            original_filename=source_path.name,
            research_class="unclassified",
            subtype=None,
            upload_date=datetime.now().isoformat(),
            file_hash=file_hash,
            status="intake",
            raw_path=str(dest_path),
            notes=notes
        )
        
        self.registry[doc_id] = doc
        self._save_registry()
        
        return doc
    
    def update_classification(
        self,
        doc_id: str,
        research_class: ResearchClass,
        subtype: Optional[str] = None,
        confidence: float = 1.0
    ):
        """
        Step 2: CLASSIFY - Record AI's classification decision.
        
        This is called after AI analyzes the document.
        Human still needs to approve before promotion.
        """
        if doc_id not in self.registry:
            raise KeyError(f"Document not found: {doc_id}")
        
        doc = self.registry[doc_id]
        doc.research_class = research_class.value
        doc.subtype = subtype
        doc.classification_confidence = confidence
        doc.status = "classified"
        
        self._save_registry()
    
    def record_digest(self, doc_id: str, digest_path: str):
        """
        Step 3: DISTILL - Record that digest has been created.
        """
        if doc_id not in self.registry:
            raise KeyError(f"Document not found: {doc_id}")
        
        doc = self.registry[doc_id]
        doc.digest_path = digest_path
        doc.status = "distilled"
        
        self._save_registry()
    
    def approve_and_place(
        self,
        doc_id: str,
        approved_by: str = "author",
        promotion_target: Optional[str] = None
    ) -> str:
        """
        Step 4: PROMOTE - Human approves and document moves to final location.
        
        Returns the final path where document was placed.
        """
        if doc_id not in self.registry:
            raise KeyError(f"Document not found: {doc_id}")
        
        doc = self.registry[doc_id]
        
        if doc.status not in ["classified", "distilled"]:
            raise ValueError(f"Document must be classified/distilled before approval")
        
        # Determine destination
        research_class = ResearchClass(doc.research_class)
        base_path = self.CLASS_PATHS[research_class]
        
        if research_class == ResearchClass.CANON:
            # Canon goes to staging first, then specific location
            if promotion_target:
                dest_dir = self.base_dir / "reference" / promotion_target
            else:
                dest_dir = self.base_dir / "research" / "canon_staging"
        else:
            dest_dir = self.base_dir / base_path
            if doc.subtype:
                dest_dir = dest_dir / doc.subtype
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Move digest (the processed version) to final location
        if doc.digest_path and Path(doc.digest_path).exists():
            digest_file = Path(doc.digest_path)
            final_path = dest_dir / f"{doc.id}_digest.md"
            shutil.copy2(digest_file, final_path)
            doc.final_path = str(final_path)
        
        # Update status
        doc.status = "approved"
        doc.approved_by = approved_by
        doc.approved_date = datetime.now().isoformat()
        doc.promotion_target = promotion_target
        
        self._save_registry()
        
        return doc.final_path or ""
    
    def reject(self, doc_id: str, reason: str = ""):
        """Reject a document - moves to rejected/"""
        if doc_id not in self.registry:
            raise KeyError(f"Document not found: {doc_id}")
        
        doc = self.registry[doc_id]
        
        # Move raw file to rejected
        raw_path = Path(doc.raw_path)
        if raw_path.exists():
            rejected_path = self.rejected_dir / raw_path.name
            shutil.move(str(raw_path), str(rejected_path))
            doc.raw_path = str(rejected_path)
        
        doc.status = "rejected"
        doc.notes = f"{doc.notes}\nRejected: {reason}".strip()
        
        self._save_registry()
    
    def get_intake_queue(self) -> List[ResearchDocument]:
        """Get documents awaiting classification."""
        return [d for d in self.registry.values() if d.status == "intake"]
    
    def get_pending_approval(self) -> List[ResearchDocument]:
        """Get documents classified but not yet approved."""
        return [d for d in self.registry.values() 
                if d.status in ["classified", "distilled"]]
    
    def get_by_class(self, research_class: ResearchClass) -> List[ResearchDocument]:
        """Get all approved documents of a specific class."""
        return [d for d in self.registry.values()
                if d.research_class == research_class.value and d.status == "approved"]
    
    def get_statistics(self) -> Dict:
        """Get intake statistics."""
        stats = {
            "total": len(self.registry),
            "by_status": {},
            "by_class": {}
        }
        
        for doc in self.registry.values():
            stats["by_status"][doc.status] = stats["by_status"].get(doc.status, 0) + 1
            if doc.research_class != "unclassified":
                stats["by_class"][doc.research_class] = stats["by_class"].get(doc.research_class, 0) + 1
        
        return stats
    
    @staticmethod
    def get_class_info(research_class: ResearchClass) -> Dict:
        """Get detailed information about a research class."""
        return RESEARCH_CLASS_INFO[research_class]


# Convenience functions for GUI

def ingest_file(filepath: str, notes: str = "", base_dir: str = ".") -> Dict:
    """Ingest a file into the intake queue."""
    service = ResearchIngestService(Path(base_dir))
    doc = service.ingest(Path(filepath), notes)
    return doc.to_dict()


def get_research_classes() -> List[Dict]:
    """Get information about all research classes for UI."""
    return [
        {
            "value": rc.value,
            **RESEARCH_CLASS_INFO[rc]
        }
        for rc in ResearchClass
    ]


def approve_document(
    doc_id: str,
    promotion_target: Optional[str] = None,
    base_dir: str = "."
) -> Dict:
    """Approve a document and place it in final location."""
    service = ResearchIngestService(Path(base_dir))
    final_path = service.approve_and_place(doc_id, promotion_target=promotion_target)
    return {"doc_id": doc_id, "final_path": final_path, "status": "approved"}
