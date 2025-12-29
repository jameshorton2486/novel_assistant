"""
Tests for settings module.
"""

import os
import pytest
import tempfile
from pathlib import Path
from utils.settings import Settings


def test_settings_default_config() -> None:
    """Test that default config is created when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        settings = Settings(config_path=config_path)
        
        assert settings.get_ai_provider() == "openai"
        assert settings.get_theme() == "light"
        assert settings.is_autosave_enabled() is True
        assert settings.use_google_drive() is True


def test_settings_get_set() -> None:
    """Test getting and setting configuration values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        settings = Settings(config_path=config_path)
        
        # Test get with default
        value = settings.get("nonexistent.key", "default")
        assert value == "default"
        
        # Test set and get
        settings.set("test.key", "test_value")
        assert settings.get("test.key") == "test_value"


def test_settings_ai_provider() -> None:
    """Test AI provider getter and setter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        settings = Settings(config_path=config_path)
        
        # Test default
        assert settings.get_ai_provider() == "openai"
        
        # Test setting to claude
        settings.set_ai_provider("claude")
        assert settings.get_ai_provider() == "claude"
        
        # Test invalid provider (should not change)
        original = settings.get_ai_provider()
        settings.set_ai_provider("invalid")
        assert settings.get_ai_provider() == original


def test_settings_theme() -> None:
    """Test theme getter and setter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        settings = Settings(config_path=config_path)
        
        # Test default
        assert settings.get_theme() == "light"
        
        # Test setting to dark
        settings.set_theme("dark")
        assert settings.get_theme() == "dark"
        
        # Test invalid theme (should not change)
        original = settings.get_theme()
        settings.set_theme("invalid")
        assert settings.get_theme() == original


def test_settings_autosave() -> None:
    """Test auto-save settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        settings = Settings(config_path=config_path)
        
        assert settings.is_autosave_enabled() is True
        assert settings.get_autosave_interval() == 60
        
        settings.set("autosave.enabled", False)
        assert settings.is_autosave_enabled() is False



