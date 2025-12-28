# Novel Assistant

An AI-assisted system for writing novels with a Python and PyQt6 interface.

## Overview

The Novel Assistant is designed to help writers create better novels through AI-powered assistance. It provides tools for generating outlines, drafting chapters, improving prose quality, and maintaining consistent voice and style throughout your work.

## Features

- **AI-Powered Writing Assistance**: Generate chapters, scenes, and character development
- **PyQt6 GUI Interface**: Full-featured writing studio with rich text editor
- **Spec-Based System**: Follows detailed specifications for consistent, high-quality output
- **Token Efficiency**: Optimized for cost-effective AI interactions
- **Multiple AI Client Support**: OpenAI and Claude (Anthropic) support
- **Google Drive Integration**: Save and load chapters directly from Google Drive

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Google Cloud credentials (for Drive integration)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/jameshorton2486/novel_assistant.git
cd novel_assistant

# 2. Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Copy .env.example to .env and add your API keys:
copy .env.example .env
# Then edit .env with your actual keys

# 5. Run the application
python main.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Google Drive Setup

1. Create a Google Cloud project at https://console.cloud.google.com/
2. Enable the Google Drive API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download `credentials.json` and place it in `credentials/credentials.json`
5. On first run, you'll be prompted to authorize the app

## Usage

### GUI Interface

Launch the full writing studio:

```bash
python main.py
```

The PyQt6 interface provides:
- **Chapter sidebar**: Browse and manage your chapters
- **Rich text editor**: Write and edit your content
- **AI Generation**: Generate new content with a prompt
- **AI Revision**: Select text and revise it with instructions
- **Google Drive sync**: Save and load chapters from the cloud

### Toolbar Actions

| Button | Function |
|--------|----------|
| New Chapter | Create a new chapter file |
| Generate | Generate new text using AI |
| Revise Selection | Revise selected text with instructions |
| Save to Drive | Save current chapter to Google Drive |
| Load from Drive | Refresh chapter list from Google Drive |

## Project Structure

```
novel_assistant/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── agent/
│   ├── __init__.py
│   ├── agent_core.py      # Core agent functionality
│   ├── claude_client.py   # Anthropic Claude API wrapper
│   ├── openai_client.py   # OpenAI API wrapper
│   ├── drive_client.py    # Google Drive integration
│   └── spec_loader.py     # Specification file loader
├── gui/
│   ├── __init__.py
│   └── app.py             # PyQt6 GUI application
├── specs/
│   ├── NOVEL_ASSISTANT_MASTER_SPEC.md
│   ├── SYSTEM_PROMPT.md
│   ├── TOKEN_STRATEGY.md
│   └── WORKFLOW_PIPELINE.md
└── credentials/           # (gitignored) Google credentials
    └── credentials.json
```

## Specifications

The assistant follows detailed specifications for consistent output:

- **NOVEL_ASSISTANT_MASTER_SPEC.md**: Core capabilities and voice guidelines
- **SYSTEM_PROMPT.md**: AI identity and responsibilities
- **TOKEN_STRATEGY.md**: Efficiency rules for AI interactions
- **WORKFLOW_PIPELINE.md**: Novel creation workflow phases

## AI Clients

### OpenAI (Default)
Uses GPT-4o for text generation and revision. Requires `OPENAI_API_KEY`.

### Claude (Anthropic)
Alternative client using Claude Sonnet. Requires `ANTHROPIC_API_KEY`.

To switch clients, modify `gui/app.py` to import `ClaudeClient` instead of `OpenAIClient`.

## Google Drive Structure

The app creates the following folder structure in your Google Drive:

```
NovelAssistant/
├── Chapters/      # Your chapter files
├── Notes/         # Story notes
└── Characters/    # Character profiles
```

## Troubleshooting

### "Missing OPENAI_API_KEY environment variable"
Ensure your `.env` file exists and contains a valid API key.

### "Missing credentials.json"
Download OAuth credentials from Google Cloud Console and place in `credentials/credentials.json`.

### Google Drive authentication fails
Delete `token.json` and re-run the app to re-authenticate.

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
