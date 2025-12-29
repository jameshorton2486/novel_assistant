"""
Settings manager for Novel Assistant.
Handles loading and saving configuration from config.yaml.
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings:
    """Manages application settings from config.yaml."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from config.yaml file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save_config()

    def save_config(self) -> None:
        """Save current configuration to config.yaml file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def _default_config(self) -> Dict[str, Any]:
        """Returns default configuration."""
        return {
            "ai": {
                "provider": "openai",
                "openai": {
                    "model": "gpt-4o",
                    "max_tokens": 4000
                },
                "claude": {
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4000
                }
            },
            "storage": {
                "use_google_drive": True,
                "local_chapters_path": "chapters"
            },
            "autosave": {
                "enabled": True,
                "interval_seconds": 60
            },
            "ui": {
                "theme": "light",
                "word_count_enabled": True,
                "show_status_bar": True
            },
            "editor": {
                "font_family": "Consolas",
                "font_size": 12,
                "wrap_mode": True
            }
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        Example: settings.get("ai.provider")
        """
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default

    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        Example: settings.set("ai.provider", "claude")
        """
        keys = key_path.split(".")
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    def get_ai_provider(self) -> str:
        """Get the current AI provider."""
        return self.get("ai.provider", "openai")

    def set_ai_provider(self, provider: str) -> None:
        """Set the AI provider (openai or claude)."""
        if provider in ["openai", "claude"]:
            self.set("ai.provider", provider)

    def get_theme(self) -> str:
        """Get the current theme."""
        return self.get("ui.theme", "light")

    def set_theme(self, theme: str) -> None:
        """Set the theme (light or dark)."""
        if theme in ["light", "dark"]:
            self.set("ui.theme", theme)

    def is_autosave_enabled(self) -> bool:
        """Check if auto-save is enabled."""
        return self.get("autosave.enabled", True)

    def get_autosave_interval(self) -> int:
        """Get auto-save interval in seconds."""
        return self.get("autosave.interval_seconds", 60)

    def use_google_drive(self) -> bool:
        """Check if Google Drive should be used."""
        return self.get("storage.use_google_drive", True)

    def get_local_chapters_path(self) -> str:
        """Get the local chapters directory path."""
        return self.get("storage.local_chapters_path", "chapters")

