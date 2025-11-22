#!/usr/bin/env python3
"""
Unit tests for AI/LLM integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hub'))

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil
from hub.ai_llm import OllamaClient


class TestOllamaClient(unittest.TestCase):
    """Test OllamaClient functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.scripts_dir = os.path.join(self.test_dir, "scripts")
        self.logs_dir = os.path.join(self.test_dir, "logs")
        os.makedirs(self.scripts_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('os.makedirs')
    def test_client_initialization(self, mock_makedirs):
        """Test that client initializes with correct host."""
        client = OllamaClient(host="http://test.example.com:11434")
        self.assertEqual(client.host, "http://test.example.com:11434")
    
    @patch('os.makedirs')
    def test_client_initialization_default_host(self, mock_makedirs):
        """Test that client uses default host from environment."""
        with patch.dict(os.environ, {'OLLAMA_HOST': 'http://custom.host:11434'}):
            client = OllamaClient()
            self.assertEqual(client.host, "http://custom.host:11434")
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.requests.get')
    def test_check_connection_success(self, mock_get, mock_makedirs):
        """Test successful connection check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        result = client.check_connection()
        
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.requests.get')
    def test_check_connection_failure(self, mock_get, mock_makedirs):
        """Test failed connection check."""
        mock_get.side_effect = Exception("Connection refused")
        
        client = OllamaClient()
        result = client.check_connection()
        
        self.assertFalse(result)
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.requests.get')
    def test_list_models(self, mock_get, mock_makedirs):
        """Test listing available models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [
                {'name': 'llama3.1:8b'},
                {'name': 'dolphin-llama3:8b'}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        models = client.list_models()
        
        self.assertEqual(len(models), 2)
        self.assertIn('llama3.1:8b', models)
        self.assertIn('dolphin-llama3:8b', models)
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.requests.post')
    @patch('hub.ai_llm.get_persona')
    @patch('hub.ai_llm.get_kink_zone')
    @patch('hub.ai_llm.get_safety_level')
    def test_generate_script_success(self, mock_safety, mock_zone, mock_persona, mock_post, mock_makedirs):
        """Test successful script generation."""
        # Mock persona
        mock_persona_obj = Mock()
        mock_persona_obj.name = "Test Persona"
        mock_persona_obj.description = "A test persona"
        mock_persona_obj.voice_style = "calm and soothing"
        mock_persona_obj.default_themes = ["relaxation"]
        mock_persona_obj.recommended_model = "llama3.1:8b"
        mock_persona.return_value = mock_persona_obj
        
        # Mock kink zone
        mock_zone.return_value = {
            "name": "Test Zone",
            "themes": ["theme1", "theme2"],
            "safety_level": 5
        }
        
        # Mock safety level
        mock_safety.return_value = {
            "name": "Maximum Guardrails",
            "restrictions": ["Emergency exit required"],
            "content_filter": True
        }
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'This is a test hypnotic script... [Awakening]'
        }
        mock_post.return_value = mock_response
        
        # Override directory paths for testing
        client = OllamaClient()
        client.scripts_dir = self.scripts_dir
        client.logs_dir = self.logs_dir
        
        result = client.generate_script(
            persona="test_persona",
            duration=20,
            kink_zone="test_zone",
            safety_level=5
        )
        
        # Verify result
        self.assertIn("timestamp", result)
        self.assertIn("script", result)
        self.assertEqual(result["persona"], "test_persona")
        self.assertEqual(result["duration"], 20)
        
        # Check that files were created
        script_files = os.listdir(self.scripts_dir)
        self.assertGreater(len(script_files), 0)
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.requests.post')
    @patch('hub.ai_llm.get_persona')
    @patch('hub.ai_llm.get_kink_zone')
    @patch('hub.ai_llm.get_safety_level')
    def test_generate_script_api_error(self, mock_safety, mock_zone, mock_persona, mock_post, mock_makedirs):
        """Test script generation with API error."""
        # Mock persona
        mock_persona_obj = Mock()
        mock_persona_obj.name = "Test Persona"
        mock_persona_obj.description = "A test persona"
        mock_persona_obj.voice_style = "calm"
        mock_persona_obj.default_themes = ["relaxation"]
        mock_persona_obj.recommended_model = "llama3.1:8b"
        mock_persona.return_value = mock_persona_obj
        
        # Mock kink zone
        mock_zone.return_value = {"themes": ["theme1"], "safety_level": 5}
        
        # Mock safety level
        mock_safety.return_value = {
            "name": "Maximum Guardrails",
            "restrictions": ["Emergency exit required"],
            "content_filter": True
        }
        
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        client.scripts_dir = self.scripts_dir
        
        result = client.generate_script(persona="test_persona")
        
        # Should return error
        self.assertIn("error", result)
    
    @patch('os.makedirs')
    def test_build_prompt(self, mock_makedirs):
        """Test prompt building."""
        client = OllamaClient()
        prompt = client._build_prompt(
            persona="Gentle Guide",
            duration=20,
            themes=["relaxation", "mindfulness"],
            voice_style="calm and soothing"
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("20-minute", prompt)
        self.assertIn("Gentle Guide", prompt)
        self.assertIn("relaxation", prompt)
    
    @patch('os.makedirs')
    def test_apply_content_filter(self, mock_makedirs):
        """Test content filtering."""
        client = OllamaClient()
        
        # Script without emergency exit
        script = "This is a test script."
        safety_config = {"name": "High Safety", "content_filter": True}
        
        filtered = client._apply_content_filter(script, safety_config)
        
        # Should add safety note
        self.assertIn("emergency", filtered.lower())
        self.assertIn("awaken", filtered.lower())
    
    @patch('os.makedirs')
    def test_apply_content_filter_already_has_exit(self, mock_makedirs):
        """Test content filter when emergency exit already present."""
        client = OllamaClient()
        
        # Script with emergency exit
        script = "This is a test script. Wake at any time. [Awakening Sequence]"
        safety_config = {"name": "High Safety", "content_filter": True}
        
        filtered = client._apply_content_filter(script, safety_config)
        
        # Should not duplicate
        self.assertEqual(script.count("wake"), filtered.count("wake"))


class TestPromptBuilding(unittest.TestCase):
    """Test prompt building with guardrails."""
    
    @patch('os.makedirs')
    @patch('hub.ai_llm.get_persona')
    @patch('hub.ai_llm.get_safety_level')
    def test_build_prompt_with_guardrails(self, mock_safety, mock_persona, mock_makedirs):
        """Test building prompt with safety guardrails."""
        mock_persona_obj = Mock()
        mock_persona_obj.name = "Test Persona"
        mock_persona_obj.description = "A test"
        mock_persona.return_value = mock_persona_obj
        
        mock_safety.return_value = {
            "restrictions": [
                "Emergency exit required",
                "Awakening sequence required"
            ],
            "content_filter": True
        }
        
        client = OllamaClient()
        prompt = client._build_prompt_with_guardrails(
            persona_name="Test Persona",
            persona_desc="A test persona",
            duration=20,
            themes=["relaxation"],
            voice_style="calm",
            safety_config=mock_safety.return_value
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Emergency exit required", prompt)
        self.assertIn("Awakening sequence required", prompt)
        self.assertIn("20-minute", prompt)


if __name__ == "__main__":
    unittest.main()
