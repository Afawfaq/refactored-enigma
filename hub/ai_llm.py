#!/usr/bin/env python3
"""
Hypno Hub AI/LLM Integration
Connects to Ollama for dynamic script generation with persona support.
"""

import os
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Import persona management
try:
    from personas import (
        get_persona, get_kink_zone, get_safety_level,
        list_personas, list_kink_zones, list_models,
        PERSONAS, KINK_ZONES
    )
except ImportError:
    # Fallback if personas module not available
    PERSONAS = {}
    KINK_ZONES = {}
    def get_persona(key): return None
    def get_kink_zone(key): return None
    def get_safety_level(level): return None
    def list_personas(): return []
    def list_kink_zones(): return []
    def list_models(): return []

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
    
    def check_connection(self, retries: int = 3) -> bool:
        """
        Check if Ollama is accessible with retry logic.
        
        Args:
            retries: Number of connection attempts
            
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(retries):
            try:
                response = requests.get(f"{self.host}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Successfully connected to Ollama at {self.host}")
                    return True
                logger.warning(f"Ollama returned status {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"Connection attempt {attempt + 1}/{retries} timed out")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection attempt {attempt + 1}/{retries} failed - is Ollama running?")
            except Exception as e:
                logger.error(f"Unexpected error checking connection: {e}")
            
            if attempt < retries - 1:
                time.sleep(1)  # Wait 1 second before retry
        
        logger.error(f"Failed to connect to Ollama after {retries} attempts at {self.host}")
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
        persona: str = "gentle_guide",
        duration: int = 20,
        themes: List[str] = None,
        kink_zone: str = None,
        voice_style: str = None,
        model: str = None,
        safety_level: int = 3
    ) -> Dict[str, str]:
        """
        Generate a personalized hypnosis script using Ollama with persona support.
        
        Args:
            persona: Persona key (e.g., 'gentle_guide', 'strict_hypnotist')
            duration: Desired duration in minutes
            themes: List of themes to include (overrides persona defaults)
            kink_zone: Kink zone key (e.g., 'submission', 'transformation')
            voice_style: Voice style (overrides persona default)
            model: Ollama model to use (overrides persona recommendation)
            safety_level: Safety level 1-5 (1=minimal, 5=maximum guardrails)
            
        Returns:
            Dictionary with script content and metadata
        """
        # Load persona configuration
        persona_config = get_persona(persona)
        if not persona_config:
            persona_config = get_persona("gentle_guide")
        
        # Use persona defaults if not specified
        if not themes and kink_zone:
            zone_config = get_kink_zone(kink_zone)
            themes = zone_config.get("themes", [])[:3]  # Use first 3 themes
        elif not themes:
            themes = persona_config.default_themes
        
        if not voice_style:
            voice_style = persona_config.voice_style
        
        if not model:
            model = persona_config.recommended_model
        
        # Apply safety level
        safety_config = get_safety_level(safety_level)
        
        # Construct the prompt with guardrails
        prompt = self._build_prompt_with_guardrails(
            persona_config.name,
            persona_config.description,
            duration,
            themes,
            voice_style,
            safety_config
        )
        
        logger.info(f"Generating script: persona='{persona}', duration={duration}min, "
                   f"safety_level={safety_level}, model={model}")
        
        try:
            # Call Ollama API with timeout and error handling
            logger.info(f"Calling Ollama API with model {model} (this may take 1-2 minutes)...")
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
                timeout=180  # Increased timeout for larger models
            )
            
            if response.status_code == 200:
                result = response.json()
                script_text = result.get('response', '')
                
                # Apply post-generation guardrails if needed
                if safety_config.get("content_filter", False):
                    script_text = self._apply_content_filter(script_text, safety_config)
                
                # Save script
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_data = {
                    "timestamp": timestamp,
                    "persona": persona,
                    "persona_name": persona_config.name,
                    "duration": duration,
                    "themes": themes,
                    "kink_zone": kink_zone,
                    "voice_style": voice_style,
                    "model": model,
                    "safety_level": safety_level,
                    "safety_config": safety_config.get("name", ""),
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
                error_msg = f"Ollama API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    logger.error(f"{error_msg} - {error_detail}")
                    return {"error": f"{error_msg}: {error_detail.get('error', 'Unknown error')}"}
                except:
                    logger.error(error_msg)
                    return {"error": error_msg}
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. The AI model may be too large or the system is overloaded."
            logger.error(error_msg)
            return {"error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama. Please ensure Ollama is running."
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            logger.error(f"Unexpected error generating script: {e}", exc_info=True)
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _build_prompt(
        self,
        persona: str,
        duration: int,
        themes: List[str],
        voice_style: str
    ) -> str:
        """Build the prompt for script generation (legacy method)."""
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
    
    def _build_prompt_with_guardrails(
        self,
        persona_name: str,
        persona_desc: str,
        duration: int,
        themes: List[str],
        voice_style: str,
        safety_config: Dict
    ) -> str:
        """Build the prompt with safety guardrails applied."""
        themes_str = ", ".join(themes)
        restrictions = safety_config.get("restrictions", [])
        
        # Build system prompt based on safety level
        if safety_config.get("content_filter", True):
            system_context = "You are a skilled hypnotist who creates consensual, safe, and effective scripts."
        else:
            system_context = "You are a skilled hypnotist. Write direct, effective scripts with clear trigger words."
        
        # Build restrictions text
        restrictions_text = "\n".join([f"- {r}" for r in restrictions])
        
        prompt = f"""{system_context}

Create a {duration}-minute hypnotic script with the following parameters:

Persona: {persona_name} ({persona_desc})
Voice Style: {voice_style}
Themes: {themes_str}

Required Safety Elements:
{restrictions_text}

Additional Guidelines:
1. Start with a relaxation induction appropriate to the persona
2. Use the specified voice style consistently
3. Incorporate the themes naturally into the script
4. Use clear language and pacing indicators ("..." for pauses)
5. End with a complete awakening sequence

Format: Write as a continuous script with stage directions in [brackets].

Begin the script now:"""
        
        return prompt
    
    def _apply_content_filter(self, script: str, safety_config: Dict) -> str:
        """Apply post-generation content filtering."""
        # Basic content filtering - can be enhanced
        safety_level = safety_config.get("name", "")
        
        # Add emergency exit reminder if not present
        if "emergency" not in script.lower() and "wake" not in script.lower():
            script += "\n\n[Safety Note: You can wake at any time by saying your emergency word.]"
        
        # Ensure awakening sequence is present
        if "awaken" not in script.lower() and "wake up" not in script.lower():
            script += "\n\n[Awakening Sequence]\nSlowly returning to full awareness... counting from 1 to 5... feeling refreshed and alert... 1... 2... 3... 4... 5... fully awake now."
        
        return script
    
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
        logger.error("  ollama pull dolphin-llama3:8b")
        return
    
    # Show available personas and kink zones
    logger.info("=== Available Personas ===")
    for persona in list_personas():
        logger.info(f"  {persona['key']}: {persona['name']} (Safety: {persona['safety_level']}/5)")
    
    logger.info("\n=== Available Kink Zones ===")
    for zone in list_kink_zones():
        logger.info(f"  {zone['key']}: {zone['name']} (Safety: {zone['safety_level']}/5)")
    
    # Generate sample scripts with different personas
    logger.info("\n=== Generating Sample Scripts ===")
    
    # Example 1: Safe, therapeutic script
    logger.info("\n1. Generating safe therapeutic script...")
    result1 = client.generate_script(
        persona="gentle_guide",
        duration=15,
        kink_zone="relaxation",
        safety_level=5
    )
    if "error" not in result1:
        logger.info(f"✓ Generated: {result1['persona_name']} script")
    
    # Example 2: Medium safety kink script
    logger.info("\n2. Generating submission-themed script...")
    result2 = client.generate_script(
        persona="gentle_domme",
        duration=20,
        kink_zone="submission",
        safety_level=3
    )
    if "error" not in result2:
        logger.info(f"✓ Generated: {result2['persona_name']} script")
    
    # Example 3: Low safety uncensored script
    logger.info("\n3. Generating advanced transformation script...")
    result3 = client.generate_script(
        persona="bimbo_coach",
        duration=25,
        kink_zone="transformation",
        model="dolphin-llama3:8b",  # Uncensored model
        safety_level=2
    )
    if "error" not in result3:
        logger.info(f"✓ Generated: {result3['persona_name']} script")
    else:
        logger.warning(f"Could not generate script: {result3['error']}")
        logger.info("Tip: Pull uncensored model with: ollama pull dolphin-llama3:8b")
    
    logger.info("\n=== Script Generation Complete ===")
    logger.info("Check ./hub/scripts/ for generated files")


if __name__ == "__main__":
    main()
