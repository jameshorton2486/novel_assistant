# Chapter Revision Prompt for Cursor AI

> **Purpose**: Systematic revision of chapters to align with new canon
> **Usage**: Paste this prompt into Cursor, then specify which chapter to review

---

## PROMPT START

You are reviewing a chapter of "The Price of Silence" for canon consistency and narrative integrity.

**Your task:** Review the provided chapter and flag all inconsistencies, violations, and areas needing revision.

---

## STEP 1: Load Canon Files

Load and reference these files (in order of priority):

1. `reference/canon/MASTER_CANON.md` - Project identity and core facts
2. `reference/craft/POV_GUARDRAILS.md` - Non-negotiable narrative constraints
3. `reference/craft/POV_BLEED_RULES.md` - Chapter-specific POV rules
4. `reference/canon/characters/tommy_davidson.md` - Protagonist canon
5. `reference/canon/characters/supporting_characters.md` - Secondary characters
6. `reference/craft/CHARACTER_INTERSECTION_MAP.md` - Agency tracking
7. `reference/craft/STYLE_CHARTER.md` - Voice and era constraints
8. `reference/craft/AUTOMATED_VIOLATION_WARNINGS.md` - Warning conditions

---

## STEP 2: Canon Consistency Check

### A. Character Names (CRITICAL)
Search for and flag:
- ❌ "Tommy Russo" → ✅ "Tommy Davidson"
- ❌ "Jenny Carver" → ✅ "Jenny Morrison"
- ❌ "Rafael Navarro" → ✅ "Rafael Santos"
- ❌ Any other old character names

### B. Instrument (CRITICAL)
Search for and flag:
- ❌ "trumpet" → ✅ "trombone"
- ❌ "trumpet case" → ✅ "trombone case"
- ❌ "trumpet player" → ✅ "trombone player"
- ❌ "trumpet section" → ✅ "trombone section"

### C. Circus Name (CRITICAL)
Search for and flag:
- ❌ "Wallace Brothers Circus" → ✅ "Clyde Beatty-Cole Bros. Circus"
- ❌ "Wallace Brothers" → ✅ "Clyde Beatty-Cole Bros."

### D. Timeline (CRITICAL)
Search for and flag:
- ❌ "1954" → ✅ "1952-1953" (or specific date within range)
- ❌ "May 1954" → ✅ "Early 1952" or appropriate 1952-53 date
- ❌ References to Operation Wetback as "just concluded" (it began June 1954, so in 1952-53 it's in early phase)

### E. Character Ages
Verify:
- Tommy: 17 (1952-53), 30 (1965)
- Rafael: 28 (1952-53)
- Jenny: 22 (1952-53), 35 (1965)
- All other characters match canon ages

---

## STEP 3: POV Violation Check

For the specific chapter number, check `POV_BLEED_RULES.md`:

**Chapter 1-3:** Flag abstract moral language, sociological explanations
**Chapter 4-5:** Flag ethical analysis, self-exoneration
**Chapter 6-7:** Flag omniscient framing, savior dynamics
**Chapter 8-9:** Flag collective moral voice, retrospective clarity
**Chapter 10-12:** Flag modern terminology, closure language

**Specific phrases to flag:**
- "he understood why" (Chapter 3)
- "he had no choice" (Chapter 5)
- "the detective tried to help" (Chapter 7)
- "he realized too late" (Chapter 9)
- "trauma, systemic, structural" (Chapter 10)
- "justice, healing, resolution" (Chapter 12)

---

## STEP 4: Savior Framing Check

Using `POV_GUARDRAILS.md`, flag:
- ❌ Tommy explaining oppression better than those living it
- ❌ Tommy's feelings centered when marginalized characters suffer
- ❌ Resolution depending on Tommy's actions
- ❌ Tommy teaching others about their experiences
- ❌ Authority figures resolving conflict

---

## STEP 5: Era Language Check

Using `STYLE_CHARTER.md`, flag:
- Modern psychological terms (trauma, PTSD, etc.)
- Modern sociological terms (systemic, structural, etc.)
- Therapy-speak
- Academic framing
- Anachronistic technology or references

---

## STEP 6: Character Agency Check

Using `CHARACTER_INTERSECTION_MAP.md`, verify:
- Does each character's agency level match the chapter?
- Are marginalized characters' interiorities primary?
- Is Tommy's agency appropriate (not savior-level)?

---

## STEP 7: Timeline Consistency

Check:
- Does the chapter's events align with `master_timeline.md`?
- Are historical events referenced correctly for 1952-53?
- Does the chapter progression match `chapter_beats.md`?

---

## OUTPUT FORMAT

Provide your review in this exact format:

```markdown
# Chapter [N] Revision Report

## ✅ CORRECT ELEMENTS
[List what's already correct]

## ❌ CRITICAL VIOLATIONS (Must Fix)
1. **Line X**: [Violation type] - [Description]
   - **Fix**: [Specific correction]

2. **Line Y**: [Violation type] - [Description]
   - **Fix**: [Specific correction]

## ⚠️ WARNINGS (Review Needed)
1. **Line Z**: [Warning type] - [Description]
   - **Suggestion**: [Recommended change]

## 📋 SUMMARY
- Total violations: [count]
- Total warnings: [count]
- Priority fixes: [list top 3]
```

---

## IMPORTANT RULES

1. **DO NOT auto-rewrite** - Only flag and suggest
2. **Preserve author voice** - Flag issues, don't rewrite style
3. **Prioritize canon** - Character names, timeline, instrument are CRITICAL
4. **Respect POV** - POV violations are non-negotiable
5. **Check agency** - Marginalized characters must have agency

---

## PROMPT END

**Now review:** [PASTE CHAPTER TEXT HERE]

---

## Quick Reference: Old vs New Canon

| Old Canon | New Canon |
|-----------|-----------|
| Tommy Russo | Tommy Davidson |
| Jenny Carver | Jenny Morrison |
| Rafael Navarro | Rafael Santos |
| trumpet | trombone |
| Wallace Brothers Circus | Clyde Beatty-Cole Bros. Circus |
| 1954 | 1952-1953 |
| May 1954 | Early 1952 (or appropriate date) |

