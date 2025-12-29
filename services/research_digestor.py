"""
Research Digestor - Processes and classifies research documents.

Pipeline: Ingest → Classify → Distill → Promote → Govern

CRITICAL RULE: AI does not research. AI only organizes, analyzes,
and reasons over curator-approved material.
"""

import json
import shutil
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class ResearchClass(Enum):
    """The four classes of research material."""
    CANON = "canon"           # Sacred - always loaded in AI context
    CONTEXT = "context"       # Background - when relevant
    ARTIFACT = "artifact"     # Triggers - scene-specific objects
    CRAFT = "craft"           # Meta-guidance - editorial only


class ResearchStatus(Enum):
    """Processing status of research documents."""
    UNPROCESSED = "unprocessed"
    CLASSIFIED = "classified"
    DISTILLED = "distilled"
    PROMOTED = "promoted"
    REJECTED = "rejected"


class ResearchIntent(Enum):
    """User-assigned intent during intake."""
    HISTORICAL_CONTEXT = "historical_context"    # Period facts
    LOCATION_REFERENCE = "location_reference"    # Places, geography
    CHARACTER_BACKGROUND = "character_background" # Biographies, traits
    THEMATIC = "thematic"                        # Moral themes
    STYLISTIC = "stylistic"                      # Voice, tone
    PLANNING = "planning"                        # Outlines (not for AI)


class ResearchDigestor:
    """
    Manages research document lifecycle.
    
    CRITICAL: This system ensures AI only works with curator-approved
    material. AI is FORBIDDEN from:
    - Adding facts
    - Filling gaps  
    - Web research
    - Speculation
    
    Usage:
        digestor = ResearchDigestor("/path/to/novel_assistant")
        
        # Ingest new document
        doc = digestor.ingest("/path/to/research.pdf", ResearchIntent.HISTORICAL_CONTEXT)
        
        # Classify
        digestor.classify(doc["id"], ResearchClass.CONTEXT)
        
        # Distill (requires model router)
        digestor.distill(doc["id"], model_router)
        
        # Promote to final location
        digestor.promote(doc["id"], ResearchClass.CANON)
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.paths = {
            "raw": self.base_path / "research" / "raw_sources",
            "digests": self.base_path / "research" / "digests",
            "artifacts": self.base_path / "research" / "artifacts",
            "craft": self.base_path / "research" / "craft",
            "rejected": self.base_path / "research" / "rejected",
            "reference": self.base_path / "reference",
        }
        
        # Ensure all directories exist
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
        
        # Metadata file
        self.metadata_file = self.base_path / "research" / "research_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load research document metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"documents": {}}
            self._save_metadata()
    
    def _save_metadata(self):
        """Save research document metadata."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_id(self, file_path: str) -> str:
        """Generate unique ID for document."""
        content = Path(file_path).read_bytes()
        return hashlib.md5(content).hexdigest()[:12]
    
    def _read_document(self, file_path: Path) -> str:
        """Read document content (supports txt, md, basic extraction)."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.txt', '.md']:
            return file_path.read_text(encoding='utf-8')
        elif suffix == '.docx':
            try:
                from docx import Document
                doc = Document(str(file_path))
                return '\n\n'.join([p.text for p in doc.paragraphs])
            except ImportError:
                return f"[DOCX file - install python-docx to extract: {file_path.name}]"
        elif suffix == '.pdf':
            return f"[PDF file - requires manual extraction: {file_path.name}]"
        else:
            return f"[Unknown format: {file_path.name}]"
    
    # -------------------------------------------------
    # STEP 1: INTAKE
    # -------------------------------------------------
    
    def ingest(self, file_path: str, intent: ResearchIntent, 
               title: str = None, notes: str = "") -> Dict:
        """
        Step 1: Intake new research document.
        
        - Copies file to raw_sources/
        - Creates metadata record
        - Sets status to UNPROCESSED
        
        Args:
            file_path: Path to the source file
            intent: User-assigned intent category
            title: Optional title (defaults to filename)
            notes: Optional notes about this document
            
        Returns:
            Document metadata record
        """
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate ID and destination
        doc_id = self._generate_id(file_path)
        dest = self.paths["raw"] / f"{doc_id}_{source.name}"
        
        # Copy file
        shutil.copy2(source, dest)
        
        # Create metadata
        now = datetime.now().isoformat()
        record = {
            "id": doc_id,
            "original_name": source.name,
            "stored_path": str(dest),
            "title": title or source.stem,
            "intent": intent.value,
            "status": ResearchStatus.UNPROCESSED.value,
            "research_class": None,
            "notes": notes,
            "ingested": now,
            "classified": None,
            "distilled": None,
            "promoted": None,
            "digest": None,
            "extracted_facts": []
        }
        
        self.metadata["documents"][doc_id] = record
        self._save_metadata()
        
        return record
    
    # -------------------------------------------------
    # STEP 2: CLASSIFICATION
    # -------------------------------------------------
    
    def classify(self, doc_id: str, research_class: ResearchClass,
                 ai_notes: str = "") -> Dict:
        """
        Step 2: Classify document.
        
        User assigns intent, this confirms classification.
        
        Args:
            doc_id: Document ID
            research_class: Canon, Context, Artifact, or Craft
            ai_notes: Optional notes from AI analysis
            
        Returns:
            Updated document record
        """
        if doc_id not in self.metadata["documents"]:
            raise KeyError(f"Document not found: {doc_id}")
        
        record = self.metadata["documents"][doc_id]
        record["research_class"] = research_class.value
        record["status"] = ResearchStatus.CLASSIFIED.value
        record["classified"] = datetime.now().isoformat()
        record["classification_notes"] = ai_notes
        
        self._save_metadata()
        return record
    
    # -------------------------------------------------
    # STEP 3: DISTILLATION
    # -------------------------------------------------
    
    def distill(self, doc_id: str, model_router, 
                novel_context: str = "") -> Dict:
        """
        Step 3: AI extracts relevant information.
        
        AI extracts ONLY:
        - Novel-relevant facts (specific to 1954, California, circus)
        - Usable constraints (rules narrative must follow)
        - Period-appropriate details (authentic 1950s texture)
        
        AI is FORBIDDEN from:
        - Adding facts
        - Filling gaps
        - Web research
        - Speculation
        
        Args:
            doc_id: Document ID
            model_router: ModelRouter instance for AI calls
            novel_context: Context about the novel for relevance filtering
            
        Returns:
            Updated document record with digest
        """
        if doc_id not in self.metadata["documents"]:
            raise KeyError(f"Document not found: {doc_id}")
        
        record = self.metadata["documents"][doc_id]
        
        # Read document content
        doc_path = Path(record["stored_path"])
        content = self._read_document(doc_path)
        
        # Build distillation prompt
        prompt = f"""You are extracting research for a 1954 California circus novel.

RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Extract ONLY facts that appear in this document
2. Do NOT add any information not present
3. Do NOT speculate or fill gaps
4. Do NOT search for additional information
5. Focus on: dates, names, locations, period details, constraints

Document Title: {record['title']}
Intent Category: {record['intent']}
Research Class: {record.get('research_class', 'unclassified')}

Novel Context: {novel_context or 'Historical fiction set May-June 1954, California circus circuit'}

DOCUMENT CONTENT:
{content[:15000]}  # Limit to avoid token overflow

Please extract:
1. FACTS: Specific verifiable facts with dates/names
2. CONSTRAINTS: Rules the novel must follow (e.g., "Operation Wetback began June 1954")
3. PERIOD DETAILS: Authentic 1950s texture (slang, prices, technology)
4. USABLE QUOTES: Direct quotes that could inform dialogue or narration

Format as JSON with these keys: facts, constraints, period_details, quotes
"""
        
        # Call AI for distillation
        try:
            from models.model_router import ModelType
            response = model_router.generate(prompt, ModelType.CLAUDE_SONNET, max_tokens=3000)
            
            # Try to parse as JSON
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    digest = json.loads(json_match.group())
                else:
                    digest = {"raw_response": response}
            except json.JSONDecodeError:
                digest = {"raw_response": response}
                
        except Exception as e:
            digest = {"error": str(e)}
        
        # Update record
        record["digest"] = digest
        record["status"] = ResearchStatus.DISTILLED.value
        record["distilled"] = datetime.now().isoformat()
        
        # Save digest to file
        digest_path = self.paths["digests"] / f"{doc_id}_digest.json"
        with open(digest_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": doc_id,
                "title": record["title"],
                "digest": digest
            }, f, indent=2)
        
        self._save_metadata()
        return record
    
    # -------------------------------------------------
    # STEP 4: PROMOTION
    # -------------------------------------------------
    
    def promote(self, doc_id: str, target: ResearchClass) -> Dict:
        """
        Step 4: Human decision on document fate.
        
        - Promote to Canon → copies to /reference/
        - Keep as Context → stays in /research/digests/
        - Store as Artifact → moves to /research/artifacts/
        - Reject → moves to /research/rejected/
        
        Args:
            doc_id: Document ID
            target: Final research class
            
        Returns:
            Updated document record
        """
        if doc_id not in self.metadata["documents"]:
            raise KeyError(f"Document not found: {doc_id}")
        
        record = self.metadata["documents"][doc_id]
        source_path = Path(record["stored_path"])
        
        # Determine destination
        if target == ResearchClass.CANON:
            dest_dir = self.paths["reference"]
        elif target == ResearchClass.CONTEXT:
            dest_dir = self.paths["digests"]
        elif target == ResearchClass.ARTIFACT:
            dest_dir = self.paths["artifacts"]
        elif target == ResearchClass.CRAFT:
            dest_dir = self.paths["craft"]
        else:
            dest_dir = self.paths["rejected"]
        
        # Copy/move file
        dest_path = dest_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        
        # Update record
        record["research_class"] = target.value
        record["status"] = ResearchStatus.PROMOTED.value
        record["promoted"] = datetime.now().isoformat()
        record["final_path"] = str(dest_path)
        
        self._save_metadata()
        return record
    
    def reject(self, doc_id: str, reason: str = "") -> Dict:
        """Reject a document (move to rejected folder)."""
        if doc_id not in self.metadata["documents"]:
            raise KeyError(f"Document not found: {doc_id}")
        
        record = self.metadata["documents"][doc_id]
        source_path = Path(record["stored_path"])
        
        dest_path = self.paths["rejected"] / source_path.name
        shutil.move(str(source_path), str(dest_path))
        
        record["status"] = ResearchStatus.REJECTED.value
        record["rejection_reason"] = reason
        record["rejected"] = datetime.now().isoformat()
        record["stored_path"] = str(dest_path)
        
        self._save_metadata()
        return record
    
    # -------------------------------------------------
    # STEP 5: GOVERNANCE
    # -------------------------------------------------
    
    def get_governed_context(self, chapter_context: Dict = None,
                             include_canon: bool = True,
                             include_context: bool = True,
                             artifact_ids: List[str] = None,
                             editorial_mode: bool = False) -> str:
        """
        Step 5: Returns AI-safe context based on governance rules.
        
        - Canon: Always included (if include_canon=True)
        - Context: Filtered by relevance (if include_context=True)
        - Artifacts: Only if specified by ID
        - Craft: Only in editorial mode
        
        Args:
            chapter_context: Dict with chapter info for relevance filtering
            include_canon: Include all canon material
            include_context: Include contextual material
            artifact_ids: Specific artifact IDs to include
            editorial_mode: Include craft/meta material
            
        Returns:
            Formatted context string for AI consumption
        """
        sections = []
        
        # Always include canon
        if include_canon:
            canon_docs = [
                doc for doc in self.metadata["documents"].values()
                if doc.get("research_class") == ResearchClass.CANON.value
                and doc.get("digest")
            ]
            
            if canon_docs:
                sections.append("## CANON (Sacred - Must Follow)")
                for doc in canon_docs:
                    sections.append(f"\n### {doc['title']}")
                    digest = doc.get("digest", {})
                    if isinstance(digest, dict):
                        for key in ["facts", "constraints"]:
                            if key in digest:
                                sections.append(f"\n**{key.title()}:**")
                                sections.append(json.dumps(digest[key], indent=2))
        
        # Include context if requested
        if include_context:
            context_docs = [
                doc for doc in self.metadata["documents"].values()
                if doc.get("research_class") == ResearchClass.CONTEXT.value
                and doc.get("digest")
            ]
            
            if context_docs:
                sections.append("\n## CONTEXT (Background - For Reference)")
                for doc in context_docs:
                    sections.append(f"\n### {doc['title']}")
                    digest = doc.get("digest", {})
                    if isinstance(digest, dict) and "period_details" in digest:
                        sections.append(json.dumps(digest["period_details"], indent=2))
        
        # Include specific artifacts
        if artifact_ids:
            artifact_docs = [
                doc for doc in self.metadata["documents"].values()
                if doc.get("id") in artifact_ids
                and doc.get("research_class") == ResearchClass.ARTIFACT.value
            ]
            
            if artifact_docs:
                sections.append("\n## ARTIFACTS (Scene-Specific)")
                for doc in artifact_docs:
                    sections.append(f"\n### {doc['title']}")
                    sections.append(doc.get("notes", ""))
        
        # Include craft only in editorial mode
        if editorial_mode:
            craft_docs = [
                doc for doc in self.metadata["documents"].values()
                if doc.get("research_class") == ResearchClass.CRAFT.value
            ]
            
            if craft_docs:
                sections.append("\n## CRAFT (Editorial Guidance)")
                for doc in craft_docs:
                    sections.append(f"\n### {doc['title']}")
                    sections.append(doc.get("notes", ""))
        
        return "\n".join(sections)
    
    # -------------------------------------------------
    # QUERY METHODS
    # -------------------------------------------------
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID."""
        return self.metadata["documents"].get(doc_id)
    
    def list_documents(self, status: ResearchStatus = None,
                       research_class: ResearchClass = None) -> List[Dict]:
        """List documents, optionally filtered."""
        docs = list(self.metadata["documents"].values())
        
        if status:
            docs = [d for d in docs if d.get("status") == status.value]
        
        if research_class:
            docs = [d for d in docs if d.get("research_class") == research_class.value]
        
        return docs
    
    def get_stats(self) -> Dict:
        """Get research processing statistics."""
        docs = list(self.metadata["documents"].values())
        
        return {
            "total": len(docs),
            "by_status": {
                status.value: len([d for d in docs if d.get("status") == status.value])
                for status in ResearchStatus
            },
            "by_class": {
                rc.value: len([d for d in docs if d.get("research_class") == rc.value])
                for rc in ResearchClass
            }
        }
