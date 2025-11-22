#!/usr/bin/env python3
"""
Unit tests for persona management system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hub'))

import unittest
from hub.personas import (
    get_persona, get_kink_zone, get_safety_level,
    list_personas, list_kink_zones, list_models,
    PERSONAS, KINK_ZONES, SAFETY_LEVELS, UNCENSORED_MODELS
)


class TestPersonas(unittest.TestCase):
    """Test persona management functions."""
    
    def test_get_persona_valid(self):
        """Test getting a valid persona."""
        persona = get_persona("gentle_guide")
        self.assertIsNotNone(persona)
        self.assertEqual(persona.name, "Gentle Guide")
        self.assertEqual(persona.safety_level, 5)
    
    def test_get_persona_invalid(self):
        """Test getting an invalid persona returns default."""
        persona = get_persona("nonexistent_persona")
        self.assertIsNotNone(persona)
        # Should return default (gentle_guide)
        self.assertEqual(persona.name, "Gentle Guide")
    
    def test_get_kink_zone_valid(self):
        """Test getting a valid kink zone."""
        zone = get_kink_zone("relaxation")
        self.assertIsNotNone(zone)
        self.assertEqual(zone["name"], "Relaxation & Mindfulness")
        self.assertEqual(zone["safety_level"], 5)
    
    def test_get_kink_zone_invalid(self):
        """Test getting an invalid kink zone returns default."""
        zone = get_kink_zone("nonexistent_zone")
        self.assertIsNotNone(zone)
        # Should return default (relaxation)
        self.assertEqual(zone["name"], "Relaxation & Mindfulness")
    
    def test_get_safety_level_valid(self):
        """Test getting a valid safety level."""
        safety = get_safety_level(3)
        self.assertIsNotNone(safety)
        self.assertEqual(safety["name"], "Medium Guardrails")
        self.assertTrue(safety["content_filter"])
    
    def test_get_safety_level_invalid(self):
        """Test getting an invalid safety level returns max safety."""
        safety = get_safety_level(99)
        self.assertIsNotNone(safety)
        # Should return level 5 (maximum safety)
        self.assertEqual(safety["name"], "Maximum Guardrails")
    
    def test_list_personas(self):
        """Test listing all personas."""
        personas = list_personas()
        self.assertIsInstance(personas, list)
        self.assertGreater(len(personas), 0)
        
        # Check structure
        for persona in personas:
            self.assertIn("key", persona)
            self.assertIn("name", persona)
            self.assertIn("description", persona)
            self.assertIn("safety_level", persona)
            self.assertIn("model", persona)
    
    def test_list_kink_zones(self):
        """Test listing all kink zones."""
        zones = list_kink_zones()
        self.assertIsInstance(zones, list)
        self.assertGreater(len(zones), 0)
        
        # Check structure
        for zone in zones:
            self.assertIn("key", zone)
            self.assertIn("name", zone)
            self.assertIn("description", zone)
            self.assertIn("safety_level", zone)
            self.assertIn("themes", zone)
    
    def test_list_models(self):
        """Test listing all models."""
        models = list_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        
        # Check structure
        for model in models:
            self.assertIn("name", model)
            self.assertIn("size", model)
            self.assertIn("vram", model)
            self.assertIn("speed", model)
            self.assertIn("best_for", model)
    
    def test_persona_data_integrity(self):
        """Test that all personas have required fields."""
        for key, persona in PERSONAS.items():
            self.assertIsNotNone(persona.name)
            self.assertIsNotNone(persona.description)
            self.assertIsNotNone(persona.voice_style)
            self.assertIsInstance(persona.default_themes, list)
            self.assertIn(persona.safety_level, [1, 2, 3, 4, 5])
            self.assertIsNotNone(persona.recommended_model)
    
    def test_kink_zone_data_integrity(self):
        """Test that all kink zones have required fields."""
        for key, zone in KINK_ZONES.items():
            self.assertIn("name", zone)
            self.assertIn("themes", zone)
            self.assertIn("safety_level", zone)
            self.assertIn("description", zone)
            self.assertIsInstance(zone["themes"], list)
            self.assertIn(zone["safety_level"], [1, 2, 3, 4, 5])
    
    def test_safety_level_data_integrity(self):
        """Test that all safety levels have required fields."""
        for level, config in SAFETY_LEVELS.items():
            self.assertIn("name", config)
            self.assertIn("description", config)
            self.assertIn("restrictions", config)
            self.assertIn("content_filter", config)
            self.assertIn("warning", config)
            self.assertIsInstance(config["restrictions"], list)
            self.assertIsInstance(config["content_filter"], bool)
    
    def test_persona_safety_level_mapping(self):
        """Test that personas with different safety levels exist."""
        safety_levels = [p.safety_level for p in PERSONAS.values()]
        # Should have personas at different safety levels
        self.assertIn(5, safety_levels)  # Maximum safety
        self.assertIn(2, safety_levels)  # Low safety


class TestPersonaSafetyLogic(unittest.TestCase):
    """Test safety-related logic."""
    
    def test_high_safety_personas_use_safe_models(self):
        """Test that high safety personas recommend safe models."""
        safe_personas = ["gentle_guide", "sleep_specialist", "therapist"]
        for key in safe_personas:
            persona = get_persona(key)
            self.assertEqual(persona.safety_level, 5)
            # Should recommend censored model
            self.assertEqual(persona.recommended_model, "llama3.1:8b")
    
    def test_low_safety_personas_use_uncensored_models(self):
        """Test that low safety personas recommend uncensored models."""
        persona = get_persona("bimbo_coach")
        self.assertEqual(persona.safety_level, 2)
        # Should recommend uncensored model (not the safe censored one)
        self.assertNotEqual(persona.recommended_model, "llama3.1:8b")
    
    def test_safety_level_has_emergency_exit(self):
        """Test that all safety levels require emergency exit."""
        for level, config in SAFETY_LEVELS.items():
            restrictions = config["restrictions"]
            # Every level must have emergency exit
            self.assertTrue(
                any("emergency exit" in r.lower() for r in restrictions),
                f"Safety level {level} missing emergency exit requirement"
            )


if __name__ == "__main__":
    unittest.main()
