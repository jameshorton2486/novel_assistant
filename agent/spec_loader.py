import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def load_file(path: str) -> str:
    """Load a file and return its contents."""
    if not os.path.exists(path):
        logger.warning(f"Missing file: {path}")
        return f"[Missing file: {path}]"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"Loaded file: {path}")
        return content
    except Exception as e:
        logger.error(f"Error loading file {path}: {e}")
        return f"[Error loading file: {path}]"


def load_all_specs() -> Dict[str, str]:
    """
    Loads all specification markdown files from /specs.
    Returns a dict with full text for each file.
    """
    base = os.path.join(os.path.dirname(__file__), "..", "specs")

    specs = {
        "master_spec": load_file(os.path.join(base, "NOVEL_ASSISTANT_MASTER_SPEC.md")),
        "system_prompt": load_file(os.path.join(base, "SYSTEM_PROMPT.md")),
        "token_strategy": load_file(os.path.join(base, "TOKEN_STRATEGY.md")),
        "workflow": load_file(os.path.join(base, "WORKFLOW_PIPELINE.md")),
    }
    
    logger.info(f"Loaded {len(specs)} specification files")
    return specs
