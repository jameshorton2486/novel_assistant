"""
Novel Assistant v3.1 Services
=============================

Production-grade editorial operating system with
four-class research governance.

Classes:
- CANON: Sacred facts (always loaded, never contradicted)
- CONTEXT: Background material (plausibility, never narrated)
- ARTIFACT: Scene triggers (never summarized generically)
- CRAFT: Writing guidance (revision mode only)

Core Rule: AI does not research. AI only organizes curator-approved material.
"""

# Research Pipeline
from .research_ingest import (
    ResearchIngestService,
    ResearchClass,
    ResearchDocument,
    ingest_file,
    get_research_classes,
    approve_document,
)

from .research_classifier import (
    ResearchClassifier,
    ClassificationResult,
    classify_document,
    get_subtypes,
)

from .research_digestor import (
    ResearchDigestor,
    DigestResult,
    distill_document,
)

# Reference Loading
from .reference_loader import (
    ReferenceLoader,
    LoadingContext,
    LoadedReference,
    load_reference,
    get_loading_contexts,
)

# Editorial Tools
from .advisor_mode import (
    AdvisorMode,
    AdvisorReport,
    check_chapter_consistency,
    check_chapter_style,
)

# Backup & Export
from .google_drive_sync import (
    GoogleDriveSync,
    backup_to_drive,
)

from .export_pipeline import (
    export_manuscript,
    ManuscriptNormalizer,
    ExportBuilder,
    BookMetadata,
)

from .era_linter import (
    EraLinter,
    LintIssue,
    lint_chapter,
    lint_text,
    lint_all_chapters,
)

# Phase 2: Quality Intelligence
from .metadata_extractor import (
    MetadataExtractor,
    ChapterMetadata,
    extract_chapter_metadata,
    extract_all_metadata,
    get_timeline,
)

from .arc_tracker import (
    ArcTracker,
    CharacterArc,
    ArcStage,
    get_character_arc,
    get_arc_report,
    check_arc_issues,
)

# Phase 2: Publishing
from .query_builder import (
    QueryBuilder,
    QueryPackageConfig,
    build_query_package,
    list_query_packages,
)

__all__ = [
    # Research Classes
    'ResearchClass',
    'ResearchDocument',
    'ClassificationResult',
    'DigestResult',
    
    # Research Services
    'ResearchIngestService',
    'ResearchClassifier',
    'ResearchDigestor',
    
    # Reference Loading
    'ReferenceLoader',
    'LoadingContext',
    'LoadedReference',
    
    # Advisory
    'AdvisorMode',
    'AdvisorReport',
    
    # Backup/Export
    'GoogleDriveSync',
    'ExportBuilder',
    'BookMetadata',
    
    # Era Linting
    'EraLinter',
    'LintIssue',
    
    # Phase 2: Quality Intelligence
    'MetadataExtractor',
    'ChapterMetadata',
    'ArcTracker',
    'CharacterArc',
    'ArcStage',
    
    # Phase 2: Publishing
    'QueryBuilder',
    'QueryPackageConfig',
    
    # Convenience Functions
    'ingest_file',
    'classify_document',
    'distill_document',
    'approve_document',
    'load_reference',
    'check_chapter_consistency',
    'check_chapter_style',
    'backup_to_drive',
    'export_manuscript',
    'lint_chapter',
    'lint_text',
    'lint_all_chapters',
    'extract_chapter_metadata',
    'extract_all_metadata',
    'get_timeline',
    'get_character_arc',
    'get_arc_report',
    'check_arc_issues',
    'build_query_package',
    'list_query_packages',
]

__version__ = "3.2.0"
