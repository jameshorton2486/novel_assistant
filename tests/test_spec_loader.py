"""
Tests for spec_loader module.
"""

import os
import pytest
from pathlib import Path
from agent.spec_loader import load_file, load_all_specs


def test_load_file_existing(tmp_path: Path) -> None:
    """Test loading an existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content", encoding="utf-8")
    
    content = load_file(str(test_file))
    assert content == "Test content"


def test_load_file_missing() -> None:
    """Test loading a missing file."""
    content = load_file("/nonexistent/path/file.txt")
    assert "[Missing file:" in content


def test_load_all_specs() -> None:
    """Test loading all specification files."""
    specs = load_all_specs()
    
    assert isinstance(specs, dict)
    assert "master_spec" in specs
    assert "system_prompt" in specs
    assert "token_strategy" in specs
    assert "workflow" in specs
    
    # All specs should be strings
    for key, value in specs.items():
        assert isinstance(value, str), f"{key} should be a string"

