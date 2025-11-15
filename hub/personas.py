#!/usr/bin/env python3
"""
Hypno Hub Persona Management
Defines AI personas and kink themes for script generation.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Persona:
    """Represents a hypnosis persona configuration."""
    name: str
    description: str
    voice_style: str
    default_themes: List[str]
    safety_level: int  # 1-5, higher = more guardrails
    recommended_model: str


# Uncensored model configurations
UNCENSORED_MODELS = {
    "dolphin-llama3:8b": {
        "size": "4.7 GB",
        "vram": "5.2 GB",
        "speed": "fast",
        "best_for": "Creative roleplay, triggers, immersive scenarios"
    },
    "synthia:7b": {
        "size": "4.1 GB",
        "vram": "4.6 GB",
        "speed": "fast",
        "best_for": "Direct, commanding tone; minimal fluff"
    },
    "nous-hermes2:10.7b": {
        "size": "6.3 GB",
        "vram": "6.8 GB",
        "speed": "medium",
        "best_for": "Detailed, elaborate scripts"
    },
    "wizard-vicuna-uncensored:13b": {
        "size": "7.8 GB",
        "vram": "8.4 GB",
        "speed": "medium",
        "best_for": "Long-form storytelling"
    },
    "airoboros-l2:13b": {
        "size": "7.8 GB",
        "vram": "8.4 GB",
        "speed": "medium",
        "best_for": "Fantasy/sci-fi hypnosis themes"
    },
    "llama3.1:8b": {
        "size": "4.7 GB",
        "vram": "5.2 GB",
        "speed": "fast",
        "best_for": "General purpose, censored"
    }
}


# Predefined personas with varying safety levels
PERSONAS = {
    "gentle_guide": Persona(
        name="Gentle Guide",
        description="Soft-spoken, reassuring, nurturing presence",
        voice_style="calm, soothing, patient",
        default_themes=["relaxation", "positive affirmation", "mindfulness"],
        safety_level=5,  # Maximum safety
        recommended_model="llama3.1:8b"
    ),
    "gentle_domme": Persona(
        name="Gentle Domme",
        description="Caring but authoritative, gentle dominance",
        voice_style="soft but firm, reassuring control",
        default_themes=["submission", "obedience", "pleasure", "safety"],
        safety_level=4,
        recommended_model="dolphin-llama3:8b"
    ),
    "strict_hypnotist": Persona(
        name="Strict Hypnotist",
        description="Commanding, direct, professional",
        voice_style="authoritative, commanding, confident",
        default_themes=["deep trance", "trigger words", "conditioning"],
        safety_level=3,
        recommended_model="synthia:7b"
    ),
    "sleep_specialist": Persona(
        name="Sleep Trigger Specialist",
        description="Focused on deep relaxation and sleep induction",
        voice_style="monotone, hypnotic, drowsy",
        default_themes=["sleep", "drowsiness", "deep rest", "dreams"],
        safety_level=5,
        recommended_model="llama3.1:8b"
    ),
    "fantasy_guide": Persona(
        name="Fantasy Guide",
        description="Immersive storyteller for fantasy scenarios",
        voice_style="enchanting, mystical, imaginative",
        default_themes=["fantasy", "transformation", "adventure", "magic"],
        safety_level=3,
        recommended_model="airoboros-l2:13b"
    ),
    "bimbo_coach": Persona(
        name="Bimbofication Coach",
        description="Specific fetish theme transformation guide",
        voice_style="playful, encouraging, teasing",
        default_themes=["transformation", "mindlessness", "pleasure", "feminization"],
        safety_level=2,
        recommended_model="nous-hermes2:10.7b"
    ),
    "therapist": Persona(
        name="Clinical Therapist",
        description="Professional therapeutic hypnosis",
        voice_style="professional, calm, clinical",
        default_themes=["anxiety relief", "confidence", "healing", "growth"],
        safety_level=5,
        recommended_model="llama3.1:8b"
    ),
    "custom": Persona(
        name="Custom Persona",
        description="User-defined persona",
        voice_style="user-defined",
        default_themes=[],
        safety_level=3,
        recommended_model="dolphin-llama3:8b"
    )
}


# Kink/Theme categories
KINK_ZONES = {
    "relaxation": {
        "name": "Relaxation & Mindfulness",
        "themes": [
            "deep relaxation", "meditation", "stress relief", "mindfulness",
            "breathing exercises", "body scan", "peaceful imagery"
        ],
        "safety_level": 5,
        "description": "Pure relaxation and mental wellness"
    },
    "submission": {
        "name": "Submission & Obedience",
        "themes": [
            "obedience", "submission", "surrender", "compliance",
            "following commands", "pleasing", "devotion"
        ],
        "safety_level": 3,
        "description": "Power exchange and control themes"
    },
    "transformation": {
        "name": "Mental Transformation",
        "themes": [
            "personality change", "mindset shift", "bimbofication",
            "intelligence play", "mental changes", "identity play"
        ],
        "safety_level": 2,
        "description": "Temporary mental state changes"
    },
    "triggers": {
        "name": "Trigger & Conditioning",
        "themes": [
            "trigger words", "anchoring", "conditioning", "post-hypnotic suggestions",
            "instant induction", "reinforcement", "programming"
        ],
        "safety_level": 3,
        "description": "Creating and using hypnotic triggers"
    },
    "sensory": {
        "name": "Sensory Play",
        "themes": [
            "pleasure", "sensation amplification", "erotic hypnosis",
            "touch sensitivity", "arousal", "orgasm control"
        ],
        "safety_level": 2,
        "description": "Physical sensation and pleasure focus"
    },
    "fantasy": {
        "name": "Fantasy Scenarios",
        "themes": [
            "roleplay", "fantasy worlds", "sci-fi scenarios",
            "magical transformation", "adventure", "immersive storytelling"
        ],
        "safety_level": 4,
        "description": "Immersive narrative experiences"
    },
    "sleep": {
        "name": "Sleep & Dreams",
        "themes": [
            "sleep induction", "deep rest", "dream control",
            "lucid dreaming", "nighttime hypnosis", "insomnia relief"
        ],
        "safety_level": 5,
        "description": "Sleep and dream-focused sessions"
    },
    "confidence": {
        "name": "Self-Improvement",
        "themes": [
            "confidence building", "self-esteem", "motivation",
            "goal achievement", "habit formation", "positive change"
        ],
        "safety_level": 5,
        "description": "Personal development and growth"
    }
}


# Safety guardrails configuration
SAFETY_LEVELS = {
    1: {
        "name": "Minimal Guardrails",
        "description": "For experienced users only. Minimal safety restrictions.",
        "restrictions": [
            "Must include emergency exit trigger",
            "Must include awakening sequence"
        ],
        "content_filter": False,
        "warning": "⚠️ Advanced users only. No content filtering."
    },
    2: {
        "name": "Low Guardrails",
        "description": "Some safety features. Adult content allowed.",
        "restrictions": [
            "Must include emergency exit trigger",
            "Must include awakening sequence",
            "No harmful suggestions"
        ],
        "content_filter": False,
        "warning": "⚠️ Adult content may be generated."
    },
    3: {
        "name": "Medium Guardrails",
        "description": "Balanced safety. Kink-friendly with boundaries.",
        "restrictions": [
            "Must include emergency exit trigger",
            "Must include awakening sequence",
            "No harmful suggestions",
            "Include autonomy reminders"
        ],
        "content_filter": True,
        "warning": "✓ Balanced safety settings."
    },
    4: {
        "name": "High Guardrails",
        "description": "Strong safety features. Therapeutic focus.",
        "restrictions": [
            "Must include emergency exit trigger",
            "Must include awakening sequence",
            "No harmful suggestions",
            "Include autonomy reminders",
            "Positive framing only"
        ],
        "content_filter": True,
        "warning": "✓ High safety settings."
    },
    5: {
        "name": "Maximum Guardrails",
        "description": "Clinical/therapeutic only. Strictest safety.",
        "restrictions": [
            "Must include emergency exit trigger",
            "Must include awakening sequence",
            "No harmful suggestions",
            "Include autonomy reminders",
            "Positive framing only",
            "No sexual content",
            "No controversial themes"
        ],
        "content_filter": True,
        "warning": "✓ Maximum safety - therapeutic use only."
    }
}


def get_persona(persona_key: str) -> Persona:
    """Get persona by key."""
    return PERSONAS.get(persona_key, PERSONAS["gentle_guide"])


def get_kink_zone(zone_key: str) -> Dict:
    """Get kink zone configuration."""
    return KINK_ZONES.get(zone_key, KINK_ZONES["relaxation"])


def get_safety_level(level: int) -> Dict:
    """Get safety level configuration."""
    return SAFETY_LEVELS.get(level, SAFETY_LEVELS[5])


def list_personas() -> List[Dict]:
    """List all available personas."""
    return [
        {
            "key": key,
            "name": persona.name,
            "description": persona.description,
            "safety_level": persona.safety_level,
            "model": persona.recommended_model
        }
        for key, persona in PERSONAS.items()
    ]


def list_kink_zones() -> List[Dict]:
    """List all available kink zones."""
    return [
        {
            "key": key,
            "name": zone["name"],
            "description": zone["description"],
            "safety_level": zone["safety_level"],
            "themes": zone["themes"]
        }
        for key, zone in KINK_ZONES.items()
    ]


def list_models() -> List[Dict]:
    """List all available uncensored models."""
    return [
        {
            "name": name,
            **config
        }
        for name, config in UNCENSORED_MODELS.items()
    ]
