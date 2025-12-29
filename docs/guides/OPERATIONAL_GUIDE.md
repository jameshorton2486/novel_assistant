# NOVEL ASSISTANT v3.1 — OPERATIONAL GUIDE

## Core Philosophy

This system operates on one non-negotiable principle:

> **AI does not research. AI only organizes curator-approved material.**

You decide what is true. AI helps organize what matters.

---

## The Four Research Classes

Your research is governed by four classes, each with distinct AI behavior:

### 1. CANON (Sacred)
**Location**: `/reference/`
**Examples**: Character ages, timeline dates, established relationships
**AI Behavior**:
- ✅ Always loaded
- ✅ Never contradicted
- ❌ Never expanded without your approval

### 2. CONTEXT (Background)
**Location**: `/research/context/`
**Examples**: Operation Wetback details, Bracero program history, 1950s social climate
**AI Behavior**:
- ✅ Loaded for plausibility checks
- ❌ Never directly narrated to reader
- Think of this as *pressure*, not content

### 3. ARTIFACT (Scene Triggers)
**Location**: `/research/artifacts/`
**Examples**: Letters, postcards, ticket stubs, programs
**AI Behavior**:
- ✅ Used as scene triggers
- ❌ Never summarized generically
- Meaning comes from contrast, not exposition

### 4. CRAFT (Writing Guidance)
**Location**: `/research/craft/` and `/reference/style_charter.md`
**Examples**: Style guides, author influences, process docs
**AI Behavior**:
- ✅ Loaded for revision/style modes
- ❌ Never injected into narrative
- Editorial scaffolding only

---

## Research Processing Pipeline

When you upload a document:

```
1. INGEST → File goes to intake/
2. CLASSIFY → AI determines class (you confirm)
3. DISTILL → AI extracts relevant content (class-specific)
4. PROMOTE → You approve placement
5. GOVERN → System enforces usage rules
```

**Key**: Classification happens FIRST. The class determines how AI processes the document.

---

## Directory Structure

```
novel_assistant/
├── chapters/              # Your manuscript
├── reference/             # CANON (sacred, always loaded)
│   ├── master_reference.md
│   ├── style_charter.md
│   ├── characters/
│   └── locations/
├── research/
│   ├── intake/            # New uploads (awaiting classification)
│   ├── context/           # Background research (plausibility)
│   ├── artifacts/         # Scene trigger material
│   ├── craft/             # Writing guidance
│   ├── canon_staging/     # Pending promotion to reference/
│   └── rejected/          # Discarded material
├── exports/               # DOCX, EPUB output
├── reports/               # Advisory reports
└── docs/                  # Documentation
```

---

## Daily Workflow

### Morning Writing Session

1. **Load chapter context**
   - System auto-loads CANON for consistency
   - CONTEXT available for plausibility

2. **Write**
   - Use placeholders: `[RESEARCH: specific detail]`
   - Don't stop to look things up

3. **Quick check** (optional)
   - Run consistency check against CANON
   - Run style check against CRAFT

### Research Session

1. **Upload document** to `intake/`
2. **Classify** (AI suggests, you confirm)
3. **Review digest** (AI-generated summary)
4. **Approve** → Document moves to final location

### End of Day

1. **Save chapter**
2. **Backup to Drive** (one click)
3. **Review advisory suggestions**

---

## What Goes Where

| Document Type | Class | Location |
|--------------|-------|----------|
| Character bible | CANON | `reference/characters/` |
| Timeline facts | CANON | `reference/` |
| Historical research | CONTEXT | `research/context/` |
| Period newspaper clippings | ARTIFACT | `research/artifacts/` |
| Hemingway style analysis | CRAFT | `research/craft/` |
| Your workflow notes | CRAFT (or don't upload) | `research/craft/` |
| Taglines, marketing | Don't upload | Keep separate |

---

## Advisory Mode

The AI advisor ANALYZES but NEVER WRITES.

### Available Checks

| Check | Uses | Purpose |
|-------|------|---------|
| Consistency | CANON | Find contradictions |
| Plausibility | CONTEXT | Check historical accuracy |
| Style Drift | CRAFT | Find modern intrusions |
| Tension | CANON + CONTEXT | Map pacing |

### What Advisor Does NOT Do
- Generate prose
- Write dialogue
- Create scenes
- Fill gaps

---

## Canon vs. Research

| | CANON | RESEARCH |
|--|-------|----------|
| **Authority** | Absolute | Informative |
| **Source** | What you wrote | What you uploaded |
| **Conflicts** | Canon wins | Research adapts |
| **Changes** | When manuscript changes | When you approve |

**Example**:
- Research says braceros earned 30-61¢/hour
- You write Rafael earned 45¢/hour
- **Canon is now 45¢/hour** (what you wrote)

---

## Backup to Google Drive

### Setup
1. Install Google Drive for Desktop
2. App auto-detects synced folder
3. Or set path manually in settings

### Usage
- Click "Backup to Drive"
- Syncs: chapters, reference, research, exports
- Non-destructive, timestamped

---

## Export Pipeline

1. Click "Export Manuscript"
2. System normalizes chapters:
   - Removes YAML frontmatter
   - Standardizes scene breaks
   - Converts quotes
3. Builds:
   - DOCX (Word, KDP, agents)
   - EPUB (Kindle, Apple, Kobo)
4. Creates version manifest

---

## Troubleshooting

### "Where did my research go?"
- Check class-specific folders in `research/`
- Check `research/rejected/` if declined
- Raw uploads in `research/intake/`

### "AI gave wrong information"
- AI only uses what you uploaded
- Check the source digest
- Edit or reclassify as needed

### "Style checker keeps flagging my dialogue"
- Review `style_charter.md`
- Override if intentional choice
- Log exception in notes

---

## The Golden Rules

1. **You are the author** — AI is the librarian
2. **What you write IS truth** — Research only informs
3. **Classify before summarize** — Class determines treatment
4. **Approve everything** — No auto-promotion
5. **Backup daily** — One click

---

*Novel Assistant v3.1 — Research Governance Edition*
