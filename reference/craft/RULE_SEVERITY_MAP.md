# RULE_SEVERITY_MAP.md

> **Purpose**: Classifies all governance rules by severity for export blocking and review prioritization
> **Classification**: CRAFT (governance system)
> **Usage**: Used by export validation, review systems, and AI assistants

---

## Severity Levels

### 🔴 HARD_FAILURE (Blocks Export)
Violations that break the book's ethical, historical, or narrative integrity. These must be fixed before export.

### 🟡 WARNING (Non-Blocking)
Craft issues that should be addressed but don't prevent export. These are quality concerns.

### 🟢 ADVISORY (Informational)
Optional improvements for stylistic refinement. These are suggestions, not requirements.

---

## POV_GUARDRAILS.md Classifications

### Rule 1: No Savior Framing
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- No character rescues, redeems, or morally elevates an oppressed group
- Aid may occur, but never as narrative resolution
- Change comes from systems, time, or collective pressure — not individuals

**Why HARD_FAILURE:** Core ethical violation. Breaks the novel's moral framework.

---

### Rule 2: Power Awareness
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Characters cannot transcend their historical power position
- Good intentions do not equal agency
- Silence, fear, and compromise are valid outcomes

**Why HARD_FAILURE:** Historical integrity violation. Breaks realism and power dynamics.

---

### Rule 3: POV Containment
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- POV characters may only know what they plausibly know
- No omniscient moral commentary
- No hindsight framing (e.g., "history would later show")

**Why HARD_FAILURE:** Narrative structure violation. Breaks POV consistency.

---

### Rule 4: Language Discipline
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- No modern moral vocabulary
- No therapy-speak
- No academic framing

**Why HARD_FAILURE:** Era integrity violation. Breaks historical authenticity.

---

### Rule 5: Consequence Preservation
**Severity:** 🟡 WARNING

**Rules:**
- Moral actions carry cost
- Inaction carries cost
- There are no clean victories

**Why WARNING:** Important craft principle, but doesn't break narrative if occasionally missed.

---

### Red Flags (AUTO-FAIL)
**Severity:** 🔴 HARD_FAILURE

**Flags:**
- A character explaining injustice clearly to others
- A single character catalyzing systemic change
- Moral clarity replacing lived ambiguity

**Why HARD_FAILURE:** These are explicit violations of core principles.

---

## POV_BLEED_RULES.md Classifications

### Chapter 1 — Arrival / Innocence
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Abstract moral language (system, injustice, exploitation, power, rights)
- Sociological explanations
- Future-oriented judgment

**Why HARD_FAILURE:** Breaks character age/experience. Tommy is 17 and naive.

---

### Chapter 2 — Learning the Ropes
**Severity:** 🟡 WARNING

**Rules:**
- Adult authority insight
- Romanticizing hardship (dignity, resilience as themes)
- Implied moral lessons

**Why WARNING:** Craft issue. Doesn't break narrative, but weakens authenticity.

---

### Chapter 3 — First Fracture
**Severity:** 🟡 WARNING

**Rules:**
- Early moral certainty ("he understood why", "it became clear that")

**Why WARNING:** Pacing/character development issue. Important but not blocking.

---

### Chapter 4 — Witnessing Harm
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Ethical analysis
- Institutional explanation (law, justice, system, authority)

**Why HARD_FAILURE:** Breaks POV. Tommy shouldn't have this analytical capacity yet.

---

### Chapter 5 — Complicity
**Severity:** 🟡 WARNING

**Rules:**
- Self-exoneration ("he had no choice", "anyone would have done the same")
- Narrative forgiveness

**Why WARNING:** Character development issue. Important but doesn't break narrative.

---

### Chapter 6 — Escalation
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Omniscient moral framing ("broader meaning", "historical importance")

**Why HARD_FAILURE:** Breaks POV structure. Omniscient narration violates third-person limited.

---

### Chapter 7 — Authority Appears
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Savior framing via authority figures ("the detective tried to help", "he understood their suffering")

**Why HARD_FAILURE:** Core ethical violation. Authority cannot resolve conflict.

---

### Chapter 8 — Fracture Lines
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Collective moral voice ("they all knew", "everyone understood")

**Why HARD_FAILURE:** Breaks POV. Omniscient collective voice violates narrative structure.

---

### Chapter 9 — Consequence
**Severity:** 🟡 WARNING

**Rules:**
- Retrospective moral clarity ("he realized too late")

**Why WARNING:** Pacing issue. Can weaken immediacy but doesn't break narrative.

---

### Chapter 10 — Distance (1965)
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Modern terminology (trauma, systemic, structural)

**Why HARD_FAILURE:** Era integrity violation. 1965 Tommy wouldn't use 2020s terminology.

---

### Chapter 11 — Memory vs Record
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Historical summary tone ("history would show", "later generations")

**Why HARD_FAILURE:** Breaks POV. Hindsight framing violates narrative structure.

---

### Chapter 12 — Unresolved End
**Severity:** 🔴 HARD_FAILURE

**Rules:**
- Closure or redemption ("justice", "healing", "resolution")

**Why HARD_FAILURE:** Thematic violation. Novel must end with ambiguity, not closure.

---

## AUTOMATED_VIOLATION_WARNINGS.md Classifications

### POV Violations
**Severity:** 🔴 HARD_FAILURE

**Triggers:**
- Abstract moral language appears in restricted chapters
- POV character exhibits knowledge beyond experience

**Why HARD_FAILURE:** Breaks narrative structure and character consistency.

---

### Savior Framing
**Severity:** 🔴 HARD_FAILURE

**Triggers:**
- Authority figure resolves conflict
- Marginalized character agency is removed

**Why HARD_FAILURE:** Core ethical violation. Breaks the novel's moral framework.

---

### Era Language Drift
**Severity:** 🔴 HARD_FAILURE

**Triggers:**
- Modern psychological or sociological terms appear

**Why HARD_FAILURE:** Historical integrity violation. Breaks era authenticity.

---

### Omniscient Drift
**Severity:** 🔴 HARD_FAILURE

**Triggers:**
- Collective moral voice
- Historical summary tone

**Why HARD_FAILURE:** Breaks POV structure. Violates third-person limited narrative.

---

### Closure Injection
**Severity:** 🔴 HARD_FAILURE

**Triggers:**
- Explicit justice, healing, or redemption language appears

**Why HARD_FAILURE:** Thematic violation. Novel must maintain ambiguity.

---

## Summary Statistics

| Severity | Count | Percentage |
|----------|-------|------------|
| 🔴 HARD_FAILURE | 18 | 75% |
| 🟡 WARNING | 4 | 17% |
| 🟢 ADVISORY | 0 | 0% |
| **Total Rules** | **22** | **100%** |

---

## Export Validation Logic

### Pre-Export Check
1. Scan chapter for all HARD_FAILURE violations
2. If any found → **BLOCK EXPORT**
3. Generate violation report with line numbers
4. Require fixes before export allowed

### Warning Report (Non-Blocking)
1. Scan chapter for all WARNING violations
2. Generate advisory report
3. Allow export but flag for review

### Advisory Report (Optional)
1. Generate stylistic suggestions
2. Include in review but don't block

---

## Implementation Notes

### Conservative Classification
- When in doubt, classify as HARD_FAILURE
- Better to block export than allow ethical violations
- WARNING level reserved for craft issues that don't break narrative

### Rule Priority
1. Ethical violations (savior framing) = Always HARD_FAILURE
2. Historical integrity (era language) = Always HARD_FAILURE
3. POV structure (omniscient, hindsight) = Always HARD_FAILURE
4. Character development (pacing, clarity) = Usually WARNING

### Exception Handling
- Author can override HARD_FAILURE with explicit approval
- Override must be logged with reason
- System should still flag for final review

---

## Usage in Code

```python
# Example validation logic
def validate_export(chapter_text):
    hard_failures = check_hard_failures(chapter_text)
    warnings = check_warnings(chapter_text)
    
    if hard_failures:
        return {
            "status": "BLOCKED",
            "hard_failures": hard_failures,
            "warnings": warnings
        }
    else:
        return {
            "status": "ALLOWED",
            "warnings": warnings
        }
```

---

*This classification is conservative by design. When in doubt, block export rather than allow violations.*

