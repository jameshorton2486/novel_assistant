# PHASE 2 DEVELOPMENT PLAN

## Remaining Features for Novel Assistant v3.2

This document outlines the features not yet built from the Development Plan v3.
These are GUI components and medium-priority features.

---

## PRIORITY: HIGH

### 1. Research Intake GUI
**Location**: `gui/research_intake.py`
**Dependencies**: PyQt6

**Requirements**:
- Drag-and-drop file upload interface
- File type detection (PDF, DOCX, MD, TXT)
- Classification preview (AI suggests, user confirms)
- Batch processing for multiple documents
- Progress indicator for large uploads
- Integration with `services/research_ingest.py`

**UI Components**:
```
┌─────────────────────────────────────────────┐
│  RESEARCH INTAKE                            │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐    │
│  │                                     │    │
│  │     Drop files here or click       │    │
│  │         to browse                   │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  INTAKE QUEUE (3 files)                     │
│  ┌─────────────────────────────────────┐    │
│  │ ☐ operation_wetback.pdf    CONTEXT │    │
│  │ ☐ character_notes.docx     CANON   │    │
│  │ ☐ hemingway_style.md       CRAFT   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [ Classify Selected ]  [ Process All ]     │
└─────────────────────────────────────────────┘
```

**Workflow**:
1. User drops files → Files go to `research/intake/`
2. Click "Classify" → AI suggests class (Canon/Context/Artifact/Craft)
3. User confirms/overrides → Classification saved
4. Click "Process" → Digestor creates summaries
5. Review digest → Approve or reject

---

### 2. Writing Studio GUI Updates
**Location**: `gui/writing_studio.py`
**Dependencies**: PyQt6

**New Features Needed**:
- Chapter state indicator (Draft/Revised/Locked/Published)
- Lock/Unlock buttons with reason dialog
- Era linter integration (highlight violations)
- Canon version display
- Research class filter in reference panel

**UI Additions**:
```
┌─────────────────────────────────────────────┐
│  Chapter 6: Breaking Point                  │
│  State: [REVISED ▼]  Words: 5,842          │
│  Canon: v2.3.1  Last lint: 2 warnings      │
├─────────────────────────────────────────────┤
│                                             │
│  [Editor Panel]                             │
│                                             │
├─────────────────────────────────────────────┤
│  Reference: [Canon ▼] [Context ▼] [Craft ▼]│
└─────────────────────────────────────────────┘
```

---

## PRIORITY: MEDIUM

### 3. Chapter Metadata Extractor
**Location**: `services/metadata_extractor.py`

**Extracts from each chapter**:
- POV character
- Location(s)
- Timeline (date/time)
- Characters present
- Artifacts mentioned
- Key events
- Word count
- Scene count

**Output**: `chapters/metadata/chapter_XX_meta.json`

**Implementation**:
```python
@dataclass
class ChapterMetadata:
    chapter_num: int
    pov: str
    locations: List[str]
    timeline: str
    characters: List[str]
    artifacts: List[str]
    key_events: List[str]
    word_count: int
    scene_count: int
    extracted_at: str
```

**Usage**:
- Consistency checking across chapters
- Timeline visualization
- Character appearance tracking

---

### 4. Narrative Arc Tracker
**Location**: `services/arc_tracker.py`

**Tracks character arcs across chapters**:

| Character | Arc | Chapters |
|-----------|-----|----------|
| Tommy | Complicity → moral awakening → consequences | 1-12 |
| Jenny | Desire → agency → trapped choices | 1-12 |
| Rafael | Dignity → sacrifice → tragedy | 1-12 |

**Features**:
- Define arc stages per character
- Mark chapter-by-chapter progression
- Visualize arc as curve
- Flag arc stalls or reversals
- Compare intended vs. actual arc

**Output**: `reports/arc_tracker.json`

---

### 5. PDF Export (Print-Ready)
**Location**: `services/pdf_export.py`
**Dependencies**: reportlab or weasyprint

**Requirements**:
- PDF/A format (archival quality)
- Proper typography (TNR or similar serif)
- Chapter title pages
- Page numbers
- Running headers
- Widow/orphan control
- Scene break formatting

**Formats**:
- 6x9 trade paperback
- 5.5x8.5 digest
- Letter size (for proofing)

---

### 6. Query Package Builder
**Location**: `services/query_builder.py`

**Generates agent submission package**:

| Component | Format | Notes |
|-----------|--------|-------|
| Query Letter | DOCX | Template with placeholders |
| Synopsis | DOCX | 1-2 page summary |
| Sample Chapters | DOCX | First 3 chapters or 50 pages |
| Comp Titles | TXT | Similar books with reasoning |
| Author Bio | TXT | Short bio template |

**Features**:
- Query letter template with fill-in fields
- Synopsis generator (AI-assisted from chapter summaries)
- Auto-format sample chapters to agent specs
- Comp title suggestions based on genre/theme
- Package as single ZIP or folder

---

## PRIORITY: LOW (Future)

### 7. Timeline Visualization
- Interactive timeline view
- Drag chapters to reorder
- Conflict detection (overlapping events)

### 8. Character Relationship Map
- Visual graph of character connections
- Relationship type labels
- Chapter-by-chapter evolution

### 9. Theme Tracker
- Tag scenes with themes
- Track theme density across chapters
- Ensure thematic balance

### 10. Word Count Analytics
- Daily/weekly writing stats
- Per-chapter trends
- Goal tracking

---

## IMPLEMENTATION SCHEDULE

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Research Intake GUI | `gui/research_intake.py` |
| 2 | Writing Studio Updates | Chapter states, linter integration |
| 3 | Metadata Extractor | `services/metadata_extractor.py` |
| 4 | Arc Tracker | `services/arc_tracker.py` |
| 5 | PDF Export | `services/pdf_export.py` |
| 6 | Query Package | `services/query_builder.py` |

---

## DEPENDENCIES TO INSTALL

```bash
# GUI
pip install PyQt6

# PDF Export
pip install reportlab
# or
pip install weasyprint

# Already required
pip install python-docx
pip install ebooklib
pip install PyMuPDF
```

---

## FILE STRUCTURE AFTER PHASE 2

```
novel_assistant/
├── gui/                    # NEW - PyQt6 interfaces
│   ├── __init__.py
│   ├── main_window.py
│   ├── research_intake.py
│   ├── writing_studio.py
│   └── chapter_browser.py
├── services/
│   ├── [existing services]
│   ├── metadata_extractor.py   # NEW
│   ├── arc_tracker.py          # NEW
│   ├── pdf_export.py           # NEW
│   └── query_builder.py        # NEW
├── governance/
│   └── [existing]
├── models/
│   └── [existing]
├── reference/
│   └── [existing]
├── research/
│   └── [existing]
├── chapters/
│   └── metadata/               # NEW - extracted metadata
├── exports/
│   └── query_packages/         # NEW - agent submissions
└── reports/
    └── [existing + arc reports]
```

---

## NEXT STEPS

To begin Phase 2, choose a starting point:

1. **Research Intake GUI** — Most impactful for processing your 45+ research documents
2. **Metadata Extractor** — Foundation for arc tracking and consistency
3. **PDF Export** — If you need print-ready output soon
4. **Query Package** — If agent submission is imminent

Recommended: Start with **Research Intake GUI** since it enables the full research governance workflow.

---

*Phase 2 Development Plan — Novel Assistant v3.2*
