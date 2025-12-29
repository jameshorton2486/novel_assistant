"""
Tests for Claude client.
"""

import os
import pytest
from unittest.mock import Mock, patch
from agent.claude_client import ClaudeClient


@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
@patch("agent.claude_client.load_all_specs")
def test_claude_client_init(mock_load_specs: Mock) -> None:
    """Test Claude client initialization."""
    mock_load_specs.return_value = {
        "system_prompt": "Test system prompt",
        "master_spec": "Test master spec"
    }
    
    with patch("agent.claude_client.Anthropic"):
        client = ClaudeClient()
        assert client.specs is not None
        assert "system_prompt" in client.system_prompt


@patch.dict(os.environ, {}, clear=True)
def test_claude_client_missing_key() -> None:
    """Test Claude client fails without API key."""
    with pytest.raises(ValueError, match="Missing ANTHROPIC_API_KEY"):
        ClaudeClient()


@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
@patch("agent.claude_client.load_all_specs")
def test_claude_generate_text(mock_load_specs: Mock) -> None:
    """Test text generation."""
    mock_load_specs.return_value = {
        "system_prompt": "Test",
        "master_spec": "Test"
    }
    
    with patch("agent.claude_client.Anthropic") as mock_anthropic:
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Generated text"
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = ClaudeClient()
        result = client.generate_text("Test prompt")
        
        assert "Generated text" in result



