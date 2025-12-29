# AI COLLABORATION WORKFLOW — THE PRICE OF SILENCE

> **Classification**: CRAFT (workflow reference)
> **Purpose**: How to use multiple AI models effectively for novel writing
> **Core Rule**: AI does not research—AI only organizes, analyzes, and reasons over curator-approved material

---

## AI Model Roles (The Writer's Room)

Think of AI models as a **writer's room** where you're the showrunner:

### Gemini — Research & Brainstorming
**Best for**: Quick historical checks, variant phrasings, cultural details, sensory descriptions

**Example prompts**:
- "Give me sensory details from circus train life in 1952–53"
- "What did a circus cookhouse smell like at dawn?"
- "Describe the sound of a calliope at the midway"

**Output**: Research packets you verify before adding to Context files

---

### Claude — Continuity Keeper
**Best for**: Holding entire manuscript + Story Bible, checking arcs, finding contradictions

**Example prompts**:
- "Check Chapter 5 against Chapter 2. Are there contradictions in Jenny's backstory?"
- "Does Tommy's emotional arc from Chapter 3 to Chapter 7 feel consistent?"
- "Review this chapter against MASTER_CANON.md for any conflicts"

**Why Claude**: Longest context window, best at nuanced analysis, maintains consistency across 60,000+ word manuscripts

---

### ChatGPT — Drafting & Polishing
**Best for**: Scene-level prose generation, rhythm, dialogue, revision passes

**Example prompts**:
- "Draft 1,200 words for Chapter 3. Begin with this postcard text, then shift to Tommy watching Jenny rehearse trapeze"
- "Rewrite this scene in Hemingway's spare style"
- "Polish this dialogue to sound more period-authentic"

**Output**: Raw draft material you edit and refine

---

## Master Prompt Template

Use this template every time you draft:

```
You are my co-author for a serious American literary novel.

The style should blend:
- Steinbeck's empathy (The Grapes of Wrath)
- Hemingway's spare power (A Farewell to Arms)
- Faulkner's layered memory (Light in August)
- Toni Morrison's lyricism (Beloved)
- Doctorow's historical moral urgency (Ragtime)

Story Bible:
[Paste MASTER_CANON.md content here]

Instructions:
1. Always keep arcs, relationships, and motifs consistent with the Bible.
2. Alternate between "Past: Circus, 1952–53" and "Present: Reflection, 1965."
3. Begin each chapter with a real postcard/letter (authentic text provided).
4. Show the gap between what letters say and what actually happened.
5. Use motifs of silence, brass music, paper artifacts, vanishing workers.
6. Target length: ~6,000 words per chapter, 12 chapters total.
7. End with Tommy's reckoning: silence broken by testimony.

Today's task:
Draft [Chapter X], about [specific beats].
Integrate the following postcard as the epigraph: [paste text].
Write 1,200 words. Stop after [specific scene point].
```

---

## Gemini Research Prompt Template

Use this when requesting research from Gemini:

```
You are my dedicated research assistant for a historical-literary 
novel set primarily in 1952–1953 in the American circus world, 
with later reflections into the civil rights era of the 1960s.

Your task is to create a well-organized, self-contained research 
document for the following topic:

[TOPIC NAME]

Instructions:
- Include a structured overview with subheadings and bullet points
- Provide both factual history (dates, events, statistics) AND 
  sensory descriptions (sights, sounds, smells, textures)
- Highlight details that could create emotional or dramatic tension
- Keep the writing accessible, vivid, and historically accurate
- This document must stand alone for my Story Bible

Please create the research document now.
```

---

## Draft in Layers

Never ask AI for "the whole book." Work in controlled passes:

### Layer 1: Scene Beats
Write 5–7 bullet points per chapter yourself

### Layer 2: Zero Draft
Let ChatGPT draft 1,000–1,500 words at a time

### Layer 3: Continuity Pass
Give Claude both draft and MASTER_CANON.md → ask it to check arcs

### Layer 4: Style Pass
Ask ChatGPT/Gemini to rewrite sections in the voice of your author blend

### Layer 5: Your Edit
**You are always the final filter**

---

## Iterative Refinement Process

1. Write **1–2k words per sitting**
2. Revise yourself first
3. Re-feed revisions to AI for polishing
4. Always keep MASTER_CANON.md updated as "canon"
5. Check against STYLE_CHARTER.md for period authenticity
6. Verify POV_GUARDRAILS.md compliance

---

## Human Editorial Control

AI gives raw material. **You**:

- Check **continuity** against canon
- Sharpen **themes** (silence → courage)
- Ensure **voice consistency** (no modern language)
- Curate the best from multiple drafts
- Protect **POV guardrails** (no savior framing)

---

## The Conductor Principle

To surpass the authors you admire:

1. **Blend strengths** (Steinbeck's empathy + Hemingway's precision + Morrison's lyricism)
2. **Anchor in truth** (your archive of 300 real postcards/letters)
3. **Exploit AI scale** (ask for 3 alternate versions of a scene, pick best parts)
4. **Keep your judgment at the center** — you're the conductor

---

## 10-Week Draft Plan

| Week | Focus | Chapters | Cumulative |
|------|-------|----------|------------|
| 1 | Setup + Ch 1 | 1 | ~6,500 words |
| 2 | Ch 2–3 | 2–3 | ~19,500 words |
| 3 | Ch 4 | 4 | ~26,000 words |
| 4 | Ch 5–6 | 5–6 | ~38,500 words |
| 5 | Ch 7 | 7 | ~45,000 words |
| 6 | Ch 8 | 8 | ~52,000 words |
| 7 | Ch 9–10 | 9–10 | ~65,000 words |
| 8 | Ch 11 | 11 | ~71,000 words |
| 9 | Ch 12 | 12 | ~78,000 words |
| 10 | Revision pass | Full manuscript | Draft complete |

---

## Session Workflow

Each writing session:

1. **Open** MASTER_CANON.md and relevant chapter file
2. **Review** where you left off
3. **Draft** 1,000–1,500 words with AI assistance
4. **Check** against canon, style charter, POV guardrails
5. **Save** and update progress tracker
6. **Note** any research gaps or continuity questions

---

*Craft reference. AI collaboration workflow for novel drafting.*
