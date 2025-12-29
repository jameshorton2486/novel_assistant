"""
Tests for OpenAI client.
"""

import os
import pytest
from unittest.mock import Mock, patch
from agent.openai_client import OpenAIClient


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("agent.openai_client.load_all_specs")
def test_openai_client_init(mock_load_specs: Mock) -> None:
    """Test OpenAI client initialization."""
    mock_load_specs.return_value = {
        "system_prompt": "Test system prompt",
        "master_spec": "Test master spec"
    }
    
    with patch("agent.openai_client.OpenAI"):
        client = OpenAIClient()
        assert client.specs is not None
        assert "system_prompt" in client.system_prompt


@patch.dict(os.environ, {}, clear=True)
def test_openai_client_missing_key() -> None:
    """Test OpenAI client fails without API key."""
    with pytest.raises(ValueError, match="Missing OPENAI_API_KEY"):
        OpenAIClient()


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("agent.openai_client.load_all_specs")
def test_openai_generate_text(mock_load_specs: Mock) -> None:
    """Test text generation."""
    mock_load_specs.return_value = {
        "system_prompt": "Test",
        "master_spec": "Test"
    }
    
    with patch("agent.openai_client.OpenAI") as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated text"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = OpenAIClient()
        result = client.generate_text("Test prompt")
        
        assert "Generated text" in result

