# Novel Assistant Writing Studio

A professional AI-powered tool for novel writing, chapter management, and automated review.

## Features

- **Chapter Management**: Upload, create, edit, and organize your novel chapters
- **Research Organization**: Store and categorize research documents
- **AI-Powered Review**: Automated chapter review for consistency, prose quality, and historical accuracy
- **Multi-Model Support**: Claude, GPT-4o, and Gemini integration
- **Token-Efficient**: Smart reference loading minimizes API costs
- **Batch Processing**: Review all chapters at once

## Quick Start

### 1. Install Dependencies

```bash
cd novel_assistant
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add at least one API key:

```bash
copy .env.example .env
# Edit .env with your API key(s)
```

**Recommended**: Use Claude (ANTHROPIC_API_KEY) for best prose quality.

### 3. Run the Application

```bash
python main.py
```

## Directory Structure

```
novel_assistant/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env                 # API keys (create from .env.example)
│
├── models/              # AI model implementations
│   ├── base_model.py    # Abstract interface
│   ├── claude_model.py  # Anthropic Claude
│   ├── openai_model.py  # OpenAI GPT
│   ├── gemini_model.py  # Google Gemini
│   └── model_router.py  # Model selection
│
├── services/            # Business logic
│   ├── reference_loader.py  # Token-efficient context loading
│   └── batch_review.py      # Multi-chapter review
│
├── gui/                 # PyQt6 interface
│   └── writing_studio.py    # Main application window
│
├── chapters/            # Your novel chapters (auto-created)
├── research/            # Research documents (auto-created)
├── reference/           # Reference files for AI context
│   ├── master_reference.md
│   ├── characters/
│   ├── locations/
│   ├── timeline/
│   └── historical/
└── reviews/             # Review outputs (auto-created)
```

## Usage Guide

### Uploading Chapters

1. Click "Upload" in the Chapters tab
2. Select your chapter files (.md, .txt, or .docx)
3. Files are copied to the `chapters/` directory

**Naming Convention**: For best results, name files like:
- `chapter_01_the_beginning.md`
- `ch2_rising_action.txt`

### Uploading Research

1. Click "Upload" in the Research tab
2. Select a category (characters, locations, historical, etc.)
3. Select your research files

### Creating Reference Files

Reference files help the AI understand your novel's context:

1. Go to the Reference tab
2. Click "Create"
3. Select a category (characters, locations, historical)
4. Enter the reference name and content

**Example Character Reference** (`reference/characters/rafael.md`):
```markdown
# Rafael Navarro

## Physical Description
- Age: 28 in 1954
- Height: 5'10"
- Build: Lean, muscular from rigging work
- Distinguishing features: Scar on left forearm, San Martín de Porres medal

## Background
- Born in Guadalajara, Mexico
- Entered US through Bracero Program in 1952
- Works as a rigger for Wallace Brothers Circus

## Personality
- Reserved, observant
- Strong moral compass
- Protective of those he cares about
- Rarely speaks unless necessary

## Key Relationships
- Tommy: Complex friendship, eventual rivalry
- Jenny: Romantic interest, protective
- Vic: Antagonistic, avoids confrontation
```

### Running Reviews

**Single Chapter Review**:
1. Load a chapter by clicking it in the list
2. Select review type (Full, Consistency, Prose, Historical)
3. Click "Review This Chapter"

**Batch Review**:
1. Select review type
2. Click "Run Batch Review"
3. Wait for all chapters to process
4. Results saved to `reviews/` directory

### AI Assistant Prompts

Use the prompt window for questions and revisions:

**Questions**:
- "Is this dialogue historically accurate for 1954?"
- "Does this scene maintain tension?"
- "Are there any anachronisms in this passage?"

**Revision Requests**:
1. Select text in the editor
2. Enter instructions like "Make the dialogue more period-appropriate"
3. Click "Revise Selection"
4. Review the response, click "Apply to Editor" if satisfied

## Token Conservation Tips

1. **Use Chapter Metadata**: Add YAML headers to chapters specifying which references are needed:
   ```yaml
   ---
   chapter: 4
   characters: [rafael, tommy, jenny]
   locations: [bakersfield]
   historical: [operation_wetback]
   ---
   ```

2. **Create Focused References**: Keep character/location refs under 500 words each

3. **Use the Right Model**:
   - Claude Haiku: Quick consistency checks (~$0.80/M tokens)
   - Claude Sonnet: Chapter revisions (~$3/M tokens)
   - Gemini 1.5 Pro: Full manuscript review (~$1.25/M tokens, 1M context)

## Model Comparison

| Model | Best For | Input Cost | Context |
|-------|----------|------------|---------|
| Claude Sonnet | Daily work, prose quality | $3/M | 200K |
| Claude Opus | Complex analysis | $15/M | 200K |
| Claude Haiku | Quick checks | $0.80/M | 200K |
| GPT-4o | Alternative to Claude | $2.50/M | 128K |
| Gemini 1.5 Pro | Full manuscript | $1.25/M | 1M |

## Troubleshooting

**"API key not configured"**
- Ensure your `.env` file exists with at least one API key
- Restart the application after editing `.env`

**"Could not load chapter"**
- Check file encoding (UTF-8 required)
- For .docx files, ensure python-docx is installed

**Reviews taking too long**
- Try Claude Haiku for faster (cheaper) reviews
- Reduce reference file sizes
- Review fewer chapters at once

## License

MIT License - See LICENSE file for details.
