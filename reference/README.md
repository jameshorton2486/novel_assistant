# Four-Class Research Governance System

## Overview

All reference material in this repository is classified into exactly one of four classes. This system ensures AI assistance remains consistent, accurate, and respectful of the author's creative authority.

**FOUNDATIONAL RULE: AI does not research—AI only organizes, analyzes, and reasons over curator-approved material.**

---

## The Four Classes

### 1. CANON (`reference/canon/`)
**Question It Answers:** "What is true in THIS novel?"

**Contents:**
- Character profiles and relationships
- Timeline of story events
- Established plot points
- Chapter summaries
- Canon version tracking

**Mutability:** Grows with chapters; sections lock after completion

**AI Behavior:** 
- **CANON IS LAW.** AI never contradicts canon.
- Canon facts override all other sources.
- When canon exists, use it. When it doesn't, flag for human decision.

---

### 2. CONTEXT (`reference/context/`)
**Question It Answers:** "What was true in 1952–53 America?"

**Contents:**
- Historical facts (Operation Wetback, Bracero Program)
- Social norms and cultural context
- Geographic information
- Industry details (circus operations)
- Terminology and period language

**Mutability:** Additive only; never contradicts canon

**AI Behavior:**
- Context CONSTRAINS plausibility but doesn't dictate plot.
- Use context to fill gaps when canon is silent.
- If canon contradicts context, canon wins (author's creative choice).

---

### 3. ARTIFACT (`reference/artifacts/`)
**Question It Answers:** "What authentic source materials exist?"

**Contents:**
- ~300 real postcards/letters from a 1950s circus musician
- Transcriptions of historical documents
- Photographs and period materials
- Real-world source material

**Mutability:** Read-only; transcriptions of real letters/postcards

**AI Behavior:**
- These are SOURCE MATERIAL, not canon until incorporated.
- Can be referenced for authenticity and inspiration.
- Never treat artifacts as established story facts.

---

### 4. CRAFT (`reference/craft/`)
**Question It Answers:** "How should this novel be written?"

**Contents:**
- Style charter (1950s voice guidelines)
- Prohibited language lists
- Literary influences (Hemingway, Steinbeck, Fitzgerald)
- Pacing guidance
- Scene checklists
- Character vocabulary guides

**Mutability:** Rare changes; governs voice and style

**AI Behavior:**
- CRAFT governs HOW to express, not WHAT to express.
- Use craft rules for prose quality, not story facts.
- Never confuse craft guidance with established canon.

---

## Classification Rules

### CANON Classification
**Use for:** Character profiles, timeline, chapter summaries, relationships, established events

**Example:** "Tommy Davidson is 17 years old in 1952" → CANON

### CONTEXT Classification
**Use for:** Historical events, social norms, industry practices, geography

**Example:** "Operation Wetback began in June 1954" → CONTEXT

### ARTIFACT Classification
**Use for:** Real postcards, letters, photographs, transcriptions

**Example:** "Letter from circus musician dated May 15, 1953" → ARTIFACT

### CRAFT Classification
**Use for:** Style guides, voice rules, prohibited terms, writing techniques

**Example:** "Never use modern therapy-speak like 'trauma' or 'triggered'" → CRAFT

---

## AI Conflict Resolution

```python
# Pseudocode for AI reference hierarchy
def resolve_conflict(canon_fact, context_fact, craft_rule):
    """
    CANON always wins over CONTEXT.
    CRAFT governs HOW to express, not WHAT to express.
    CONTEXT constrains plausibility but canon can override for story reasons.
    """
    if canon_fact exists:
        return canon_fact  # Canon is absolute
    elif context_fact exists:
        return context_fact  # Context fills gaps
    else:
        return None  # Flag for human decision
```

### Resolution Priority:
1. **CANON** - Absolute truth for this novel
2. **CONTEXT** - Historical truth (when canon is silent)
3. **ARTIFACT** - Source inspiration (not facts)
4. **CRAFT** - Expression rules (not content rules)

---

## AI Must NEVER:

- ❌ Research live (invent facts)
- ❌ Contradict canon
- ❌ Treat craft guidance as story facts
- ❌ Confuse optional ideas with established canon
- ❌ Use artifacts as if they were canon
- ❌ Override canon with context

---

## File Organization

```
reference/
├── canon/              # What is true in THIS novel
│   ├── characters/     # Character profiles
│   ├── timeline/       # Story timeline
│   ├── canon_version.json
│   └── canon_changelog.md
├── context/            # What was true in 1952-53 America
│   ├── terminology.md  # Period language
│   └── historical/     # Historical facts
├── artifacts/          # Authentic source materials
│   └── [postcards, letters, transcriptions]
└── craft/              # How should this novel be written
    ├── style_charter.md
    ├── scene_checklist.md
    └── vocabulary/     # Character vocabulary guides
```

---

## Usage Guidelines

1. **When writing:** Check canon first, then context for historical accuracy
2. **When researching:** Add new materials to appropriate class
3. **When revising:** Update canon only through established process
4. **When AI assists:** Always respect the hierarchy (Canon > Context > Artifact > Craft)

---

## Maintenance

- Canon changes require explicit author approval
- Context additions should be verified for historical accuracy
- Artifacts are read-only (transcriptions only)
- Craft changes are rare and require style review



