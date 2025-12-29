# AUTOMATED_VIOLATION_WARNINGS.md

This document defines **automated warning conditions** during draft review.
Warnings do NOT rewrite text automatically — they flag issues for review.

---

## POV Violations
Trigger if:
- Abstract moral language appears in restricted chapters
- POV character exhibits knowledge beyond experience

Warning:
"Possible POV bleed detected. Review narrative authority."

---

## Savior Framing
Trigger if:
- Authority figure resolves conflict
- Marginalized character agency is removed

Warning:
"Potential savior framing. Check POV_GUARDRAILS."

---

## Era Language Drift
Trigger if:
- Modern psychological or sociological terms appear

Warning:
"Era-inappropriate language detected."

---

## Omniscient Drift
Trigger if:
- Collective moral voice
- Historical summary tone

Warning:
"Omniscient narration detected. Scene may exceed POV limits."

---

## Closure Injection
Trigger if:
- Explicit justice, healing, or redemption language appears

Warning:
"Narrative closure may violate intended ambiguity."

---

## Review Output Format
Warnings should be returned as:

- Chapter
- Line or paragraph reference
- Violation type
- Suggested corrective action

No automatic rewriting unless explicitly requested.

