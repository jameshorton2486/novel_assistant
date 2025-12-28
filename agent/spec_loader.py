import os


def load_file(path):
    if not os.path.exists(path):
        return f"[Missing file: {path}]"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_all_specs():
    """
    Loads all specification markdown files from /specs.
    Returns a dict with full text for each file.
    """

    base = os.path.join(os.path.dirname(__file__), "..", "specs")

    return {
        "master_spec": load_file(os.path.join(base, "NOVEL_ASSISTANT_MASTER_SPEC.md")),
        "system_prompt": load_file(os.path.join(base, "SYSTEM_PROMPT.md")),
        "token_strategy": load_file(os.path.join(base, "TOKEN_STRATEGY.md")),
        "workflow": load_file(os.path.join(base, "WORKFLOW_PIPELINE.md")),
    }
