#!/usr/bin/env python3
"""
Hypno Hub AI/LLM Integration
Connects to Ollama for dynamic script generation.
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM on the host device."""
    
    def __init__(self, host: str = None):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama server URL (defaults to env OLLAMA_HOST or localhost)
        """
        self.host = host or os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
        self.scripts_dir = "/home/beta/hub/scripts"
        self.logs_dir = "/home/beta/hub/logs"
        
        # Ensure directories exist
        os.makedirs(self.scripts_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        logger.info(f"Initialized Ollama client with host: {self.host}")
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                logger.info(f"Available models: {models}")
                return models
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate_script(
        self,
        persona: str = "gentle guide",
        duration: int = 20,
        themes: List[str] = None,
        voice_style: str = "calm and soothing",
        model: str = "llama3.1:8b"
    ) -> Dict[str, str]:
        """
        Generate a personalized hypnosis script using Ollama.
        
        Args:
            persona: The character/role for the script
            duration: Desired duration in minutes
            themes: List of themes to include
            voice_style: Description of voice characteristics
            model: Ollama model to use
            
        Returns:
            Dictionary with script content and metadata
        """
        themes = themes or ["relaxation", "positive affirmation"]
        
        # Construct the prompt
        prompt = self._build_prompt(persona, duration, themes, voice_style)
        
        logger.info(f"Generating script with persona='{persona}', duration={duration}min")
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                script_text = result.get('response', '')
                
                # Save script
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_data = {
                    "timestamp": timestamp,
                    "persona": persona,
                    "duration": duration,
                    "themes": themes,
                    "voice_style": voice_style,
                    "model": model,
                    "script": script_text
                }
                
                # Save as JSON
                json_path = os.path.join(self.scripts_dir, f"script_{timestamp}.json")
                with open(json_path, 'w') as f:
                    json.dump(script_data, f, indent=2)
                
                # Save as plain text for easy reading
                txt_path = os.path.join(self.scripts_dir, f"script_{timestamp}.txt")
                with open(txt_path, 'w') as f:
                    f.write(script_text)
                
                logger.info(f"Script saved to {txt_path}")
                
                return script_data
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {"error": f"API returned status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return {"error": str(e)}
    
    def _build_prompt(
        self,
        persona: str,
        duration: int,
        themes: List[str],
        voice_style: str
    ) -> str:
        """Build the prompt for script generation."""
        themes_str = ", ".join(themes)
        
        prompt = f"""You are an expert in creating consensual, safe, and positive hypnotic scripts.

Create a {duration}-minute hypnotic induction script with the following parameters:

Persona: {persona}
Voice Style: {voice_style}
Themes: {themes_str}

Guidelines:
1. Start with a gentle relaxation induction
2. Use positive, affirming language throughout
3. Include breathing exercises and progressive relaxation
4. Incorporate the specified themes naturally
5. End with a gentle awakening sequence
6. Ensure all suggestions are positive and empowering
7. Include safety suggestions (ability to wake at any time, maintain autonomy)

Format the script with clear sections and natural pauses. Use "..." to indicate longer pauses.

Begin the script now:"""
        
        return prompt
    
    def generate_voice_from_script(self, script_path: str) -> Optional[str]:
        """
        Generate audio from script using TTS (placeholder for future implementation).
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Path to generated audio file or None
        """
        logger.info("Voice generation is not yet implemented")
        # Future: Integrate with Piper TTS or similar local TTS engine
        return None


def main():
    """Main function for testing the AI integration."""
    client = OllamaClient()
    
    # Check connection
    if not client.check_connection():
        logger.error("Cannot connect to Ollama. Please ensure it's running on the host.")
        logger.error(f"Expected at: {client.host}")
        return
    
    # List available models
    models = client.list_models()
    if not models:
        logger.error("No models found. Please pull a model first:")
        logger.error("  ollama pull llama3.1:8b")
        return
    
    # Generate a sample script
    logger.info("Generating sample script...")
    result = client.generate_script(
        persona="gentle guide",
        duration=20,
        themes=["relaxation", "positive affirmation", "mindfulness"],
        voice_style="calm and soothing"
    )
    
    if "error" in result:
        logger.error(f"Script generation failed: {result['error']}")
    else:
        logger.info("Script generated successfully!")
        logger.info(f"Script preview: {result['script'][:200]}...")


if __name__ == "__main__":
    main()
