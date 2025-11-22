#!/usr/bin/env python3
"""
Unit tests for Flask launcher application.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hub'))

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Mock the template files before importing launcher
from unittest.mock import mock_open

consent_html = "<html><body>Consent Page</body></html>"
configure_html = "<html><body>Configure Page</body></html>"

# Use mock_open for cleaner file mocking
with patch('builtins.open', mock_open(read_data=consent_html)):
    from hub.launcher import app


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask application routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_index_route(self):
        """Test the index (consent) route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_route(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertIn('version', data)
    
    def test_configure_route_get(self):
        """Test the configure page GET request."""
        response = self.client.get('/configure')
        self.assertIn(response.status_code, [200, 302])  # 302 if redirects
    
    @patch('hub.launcher.OllamaClient')
    @patch('hub.launcher.subprocess.Popen')
    def test_configure_route_post(self, mock_popen, mock_ollama):
        """Test the configure page POST request."""
        # Mock OllamaClient
        mock_client = Mock()
        mock_client.generate_script.return_value = {
            'timestamp': '20231201_120000',
            'script': 'Test script'
        }
        mock_ollama.return_value = mock_client
        
        response = self.client.post('/configure', data={
            'persona': 'gentle_guide',
            'kink_zone': 'relaxation',
            'model': 'llama3.1:8b',
            'safety_level': '5',
            'duration': '20'
        })
        
        # Should redirect after processing
        self.assertEqual(response.status_code, 302)
    
    @patch('hub.launcher.subprocess.Popen')
    def test_start_route(self, mock_popen):
        """Test the start session route."""
        with patch('os.path.exists', return_value=True):
            response = self.client.post('/start')
            
            # Should redirect to session page
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/session'))
    
    def test_start_route_script_not_found(self):
        """Test start route when script is missing."""
        with patch('os.path.exists', return_value=False):
            response = self.client.post('/start')
            
            # Should return error
            self.assertEqual(response.status_code, 500)
    
    def test_session_route(self):
        """Test the session active page."""
        response = self.client.get('/session')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Session Active', response.data)
    
    @patch('hub.launcher.subprocess.run')
    def test_stop_api(self, mock_run):
        """Test the stop API endpoint."""
        response = self.client.post('/api/stop')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'stopped')
        
        # Should have called pkill twice (mpv and feh)
        self.assertEqual(mock_run.call_count, 2)
    
    def test_api_personas(self):
        """Test the personas API endpoint."""
        response = self.client.get('/api/personas')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
    
    def test_api_kink_zones(self):
        """Test the kink zones API endpoint."""
        response = self.client.get('/api/kink-zones')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
    
    def test_api_models(self):
        """Test the models API endpoint."""
        response = self.client.get('/api/models')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the application."""
    
    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    @patch('hub.launcher.OllamaClient')
    def test_configure_with_ollama_error(self, mock_ollama):
        """Test configure route when Ollama returns error."""
        mock_client = Mock()
        mock_client.generate_script.return_value = {
            'error': 'Connection failed'
        }
        mock_ollama.return_value = mock_client
        
        response = self.client.post('/configure', data={
            'persona': 'gentle_guide',
            'duration': '20'
        })
        
        # Should return error status
        self.assertEqual(response.status_code, 500)
    
    @patch('hub.launcher.subprocess.run')
    def test_stop_api_with_exception(self, mock_run):
        """Test stop API when subprocess fails."""
        mock_run.side_effect = Exception("Process error")
        
        response = self.client.post('/api/stop')
        
        # Should return error status
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == "__main__":
    unittest.main()
