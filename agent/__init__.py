"""
Novel Assistant Agent Module

Contains AI clients and core functionality for the Novel Assistant.
"""

from agent.spec_loader import load_all_specs
from agent.openai_client import OpenAIClient
from agent.claude_client import ClaudeClient
from agent.drive_client import DriveClient

__all__ = [
    "load_all_specs",
    "OpenAIClient", 
    "ClaudeClient",
    "DriveClient",
]
