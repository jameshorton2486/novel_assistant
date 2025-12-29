# CURSOR AI PROMPT - Novel Assistant Customization

Use this prompt if you need Cursor AI to make additional modifications to the Novel Assistant.

---

## CONTEXT

You are working on a Python-based Novel Assistant application with:
- PyQt6 GUI for chapter/research management
- Multi-model AI support (Claude, OpenAI, Gemini)
- Batch chapter review capabilities
- Token-efficient reference loading system

The application structure:
```
novel_assistant/
├── main.py              # Entry point
├── models/              # AI model implementations
│   ├── base_model.py    # Abstract interface
│   ├── claude_model.py  # Anthropic Claude
│   ├── openai_model.py  # OpenAI GPT
│   ├── gemini_model.py  # Google Gemini
│   └── model_router.py  # Model selection & routing
├── services/            # Business logic
│   ├── reference_loader.py  # Token-efficient context loading
│   └── batch_review.py      # Multi-chapter review
├── gui/                 # PyQt6 interface
│   └── writing_studio.py    # Main window
├── chapters/            # Novel chapters
├── research/            # Research documents
├── reference/           # Reference files
└── reviews/             # Review outputs
```

## CUSTOMIZATION TASKS

### Task 1: Add Export to Google Drive

Add a button and function to export chapters/reviews to Google Drive.

Requirements:
- Use the existing `agent/drive_client.py` if available, or create new
- Add "Export to Drive" button in toolbar
- Support exporting: current chapter, all chapters, review results
- Show progress during upload

### Task 2: Add Writing Statistics Dashboard

Create a statistics panel showing:
- Total word count across all chapters
- Words per chapter (bar chart)
- Daily writing progress (if timestamps available)
- Character/location mention frequency

Requirements:
- Add as a new tab in the left panel
- Use matplotlib or PyQt6 charts
- Update automatically when chapters change

### Task 3: Add Version Control for Chapters

Implement simple version tracking:
- Auto-save versions before AI revisions
- Show version history for each chapter
- Allow restoring previous versions
- Store in `chapters/.versions/`

### Task 4: Add Custom Prompts Library

Create a library of saved prompts:
- Save frequently used prompts
- Organize by category (revision, review, research)
- Quick-insert into prompt window
- Store in `configs/prompts.json`

### Task 5: Improve Historical Accuracy Checking

Enhance the historical review mode:
- Load era-specific facts database
- Check for anachronisms automatically
- Suggest period-appropriate alternatives
- Reference specific historical sources

---

## RULES FOR MODIFICATIONS

1. **Preserve existing functionality** - Don't break what works
2. **Follow existing patterns** - Match the coding style used
3. **Add proper error handling** - Every external call needs try/except
4. **Update imports** - Add new dependencies to requirements.txt
5. **Document changes** - Add docstrings and comments
6. **Test incrementally** - Verify each change before moving on

---

## EXAMPLE MODIFICATION

To add a new AI model (e.g., Mistral):

1. Create `models/mistral_model.py`:
```python
from models.base_model import BaseModel, ModelResponse, ModelConfig

class MistralModel(BaseModel):
    # Implement all abstract methods
    ...
```

2. Register in `models/model_router.py`:
```python
MODEL_REGISTRY["mistral-large"] = {
    "class": MistralModel,
    "variant": "mistral-large-latest",
    "display_name": "Mistral Large",
    "description": "Mistral's flagship model",
    "category": "mistral"
}
```

3. Update `models/__init__.py` with new imports

4. Add API key to `.env.example`:
```
MISTRAL_API_KEY=your_key_here
```

---

## TESTING CHECKLIST

After any modification:
- [ ] Application starts without errors
- [ ] All existing buttons/menus work
- [ ] AI generation still functions
- [ ] Batch review still works
- [ ] No console errors during normal use
- [ ] New feature works as expected
