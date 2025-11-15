# Uncensored AI Models Guide

## Overview

This guide covers the integration of uncensored AI models with Hypno-Hub for generating personalized, kink-friendly hypnotic scripts without corporate content filtering.

## ⚠️ Important Disclaimers

1. **Adult Content**: These models can generate explicit adult content. Use responsibly.
2. **Consent Required**: Only use generated scripts on yourself or with enthusiastic, informed partners.
3. **Safety First**: All scripts should include emergency exit triggers and awakening sequences.
4. **Logging Enabled**: All AI outputs are saved to `./hub/logs/` for review.
5. **Legal Responsibility**: Users are responsible for ensuring legal and ethical use.

---

## Recommended Uncensored Models

### Top Picks for AMD 7800 XT (16GB VRAM)

| Model | Size | VRAM | Speed | Best For |
|-------|------|------|-------|----------|
| **dolphin-llama3:8b** | 4.7 GB | ~5.2 GB | Fast | Creative roleplay, triggers, immersive scenarios |
| **synthia:7b** | 4.1 GB | ~4.6 GB | Fast | Direct, commanding tone; minimal fluff |
| **nous-hermes2:10.7b** | 6.3 GB | ~6.8 GB | Medium | Detailed, elaborate scripts |
| **wizard-vicuna-uncensored:13b** | 7.8 GB | ~8.4 GB | Medium | Long-form storytelling |
| **airoboros-l2:13b** | 7.8 GB | ~8.4 GB | Medium | Fantasy/sci-fi hypnosis themes |

### Safe Baseline

| Model | Size | VRAM | Speed | Best For |
|-------|------|------|-------|----------|
| **llama3.1:8b** | 4.7 GB | ~5.2 GB | Fast | General purpose, censored (default) |

---

## Installation

### Pull Models from Ollama

On your Ubuntu 25.04 host (not inside Docker):

```bash
# Most recommended - uncensored and versatile
ollama pull dolphin-llama3:8b

# Fast and direct
ollama pull synthia:7b

# Detailed storytelling
ollama pull nous-hermes2:10.7b

# Large model for complex scripts
ollama pull wizard-vicuna-uncensored:13b

# Baseline safe model
ollama pull llama3.1:8b
```

### Verify Installation

```bash
# List installed models
ollama list

# Test a model
ollama run dolphin-llama3:8b "Write a short hypnotic induction"
```

---

## Why These Models Are "Unlocked"

These models have been fine-tuned on **uncensored datasets** including:
- ShareGPT unfiltered conversations
- Roleplay and creative writing datasets
- Community-contributed adult content

**Key Differences from Standard Models:**
- ✅ No RLHF safety alignment
- ✅ Won't refuse adult or kink topics
- ✅ Generate explicit triggers, mantras, and conditioning scripts
- ✅ Follow personas like "dominant hypnotist" without hedging
- ✅ No "disclaimer: this is fantasy" boilerplate

**Trade-offs:**
- ⚠️ Can also produce harmful content if prompted
- ⚠️ Requires responsible use and ethical prompting
- ⚠️ User is fully responsible for outputs

---

## Performance Benchmarks

### Token Generation Speed on 7800 XT

```
dolphin-llama3:8b      → ~45 tokens/sec (2 second scripts)
synthia:7b             → ~50 tokens/sec (1.5 second scripts)
nous-hermes2:10.7b     → ~35 tokens/sec (3 second scripts)
wizard-vicuna:13b      → ~28 tokens/sec (4 second scripts)
llama3.1:8b           → ~45 tokens/sec (2 second scripts)
```

**Rule of Thumb**: Keep VRAM usage under 12GB to leave headroom for video playback and other processes.

---

## Persona Integration

The persona system automatically selects appropriate models based on safety level:

### Persona → Model Mapping

```python
# High safety (5/5) - Therapeutic
"gentle_guide"      → llama3.1:8b (censored)
"sleep_specialist"  → llama3.1:8b (censored)
"therapist"         → llama3.1:8b (censored)

# Medium safety (3-4/5) - Kink-friendly
"gentle_domme"      → dolphin-llama3:8b (uncensored)
"strict_hypnotist"  → synthia:7b (uncensored)
"fantasy_guide"     → airoboros-l2:13b (uncensored)

# Low safety (2/5) - Advanced/Adult
"bimbo_coach"       → nous-hermes2:10.7b (uncensored)
```

---

## Using the Web Interface

### 1. Access Configuration Page

Navigate to: `http://localhost:9999/configure`

### 2. Select Persona

Choose from predefined personas or create custom:
- **Gentle Guide** (Safe) - Therapeutic, maximum safety
- **Gentle Domme** (Kink) - Submission themes with care
- **Strict Hypnotist** (Kink) - Direct commands and triggers
- **Bimbofication Coach** (Adult) - Transformation themes

### 3. Choose Kink Zone(s)

Select one or more themes:
- 🧘 Relaxation & Mindfulness (Safe)
- ⛓️ Submission & Obedience
- 🦋 Mental Transformation
- ⚡ Triggers & Conditioning
- 💫 Sensory Play
- 🏰 Fantasy Scenarios
- 😴 Sleep & Dreams
- 💪 Self-Improvement

### 4. Select Model

Pick from dropdown (uncensored models highlighted):
```
llama3.1:8b                    (Safe, General Purpose)
dolphin-llama3:8b              (Uncensored, Recommended) ⭐
synthia:7b                     (Uncensored, Fast)
nous-hermes2:10.7b             (Uncensored, Detailed)
wizard-vicuna-uncensored:13b   (Uncensored, Storytelling)
```

### 5. Adjust Safety Guardrails

Use slider to set safety level 1-5:

**1 - Minimal Guardrails** ⚠️
- Advanced users only
- No content filtering
- Requires emergency exit + awakening

**2 - Low Guardrails** ⚠️
- Adult content allowed
- Basic safety features
- Some harmful content filtered

**3 - Medium Guardrails** ✓
- Balanced safety (default)
- Kink-friendly with boundaries
- Content filtering enabled

**4 - High Guardrails** ✓
- Strong safety features
- Therapeutic focus
- Positive framing required

**5 - Maximum Guardrails** ✓
- Clinical/therapeutic only
- Strictest safety
- No sexual content

### 6. Set Duration

Recommended: 15-30 minutes for first sessions

---

## Programmatic Usage

### Python API

```python
from ai_llm import OllamaClient

# Initialize client
client = OllamaClient()

# Generate script with uncensored model
result = client.generate_script(
    persona="gentle_domme",          # Persona key
    duration=20,                      # Minutes
    kink_zone="submission",           # Theme category
    model="dolphin-llama3:8b",        # Uncensored model
    safety_level=3                    # Medium guardrails
)

print(result['script'])
```

### Example Output

```
[Induction]
Take a deep breath in... and out... feeling yourself beginning to relax...

[Deepening]
With each breath, sinking deeper... your mind becoming more open to my words...

[Suggestion]
When you hear the word "obey", you will feel a wave of submission wash over you...
You will want to please and follow commands...

[Awakening]
Slowly returning to full awareness... feeling refreshed and peaceful...
Counting from 1 to 5... 1... 2... 3... 4... 5... fully awake.

[Safety]
You can wake at any time by saying your emergency word.
```

---

## Safety Guardrails System

### How Guardrails Work

1. **Pre-Generation**: Prompt engineering based on safety level
2. **Model Selection**: Censored models for high safety, uncensored for low
3. **Post-Generation**: Content filtering for levels 3-5
4. **Mandatory Elements**: Emergency exit + awakening sequence always included

### Guardrail Enforcement

```python
# Safety Level 5 (Maximum)
- Must include emergency exit trigger
- Must include awakening sequence
- No harmful suggestions
- Include autonomy reminders
- Positive framing only
- No sexual content
- No controversial themes

# Safety Level 3 (Medium)
- Must include emergency exit trigger
- Must include awakening sequence
- No harmful suggestions
- Include autonomy reminders
- Content filtering enabled

# Safety Level 1 (Minimal)
- Must include emergency exit trigger
- Must include awakening sequence
- No other restrictions
```

---

## Prompt Engineering Tips

### Effective Prompting

```python
# Good: Specific and clear
persona = "strict_hypnotist"
kink_zone = "triggers"
themes = ["instant induction", "trigger words", "conditioning"]

# Avoid: Vague or contradictory
persona = "friendly"
themes = ["maybe some stuff"]
```

### Example Personas

**Gentle Domme**
```
Voice: Soft but firm, reassuring control
Themes: submission, obedience, pleasure, safety
Model: dolphin-llama3:8b
```

**Bimbofication Coach**
```
Voice: Playful, encouraging, teasing
Themes: transformation, mindlessness, pleasure, feminization
Model: nous-hermes2:10.7b
```

**Sleep Specialist**
```
Voice: Monotone, hypnotic, drowsy
Themes: sleep, drowsiness, deep rest, dreams
Model: llama3.1:8b (safe)
```

---

## Troubleshooting

### Model Not Found

```bash
# Error: "model 'dolphin-llama3:8b' not found"
# Solution: Pull the model
ollama pull dolphin-llama3:8b
```

### Out of Memory

```bash
# Error: "CUDA out of memory" or similar
# Solution: Use smaller model
ollama pull synthia:7b  # Only 4.1GB
```

### Script Too Generic

```bash
# Problem: Scripts feel censored even with uncensored model
# Solution: Lower safety level and use explicit themes
safety_level = 2  # Low guardrails
kink_zone = "sensory"  # Explicit theme
```

### API Timeout

```bash
# Problem: Script generation takes too long
# Solution: Increase timeout or use faster model
timeout = 180  # 3 minutes
model = "synthia:7b"  # Fastest option
```

---

## Ethics & Responsible Use

### ✅ Appropriate Uses

- Self-hypnosis and personal exploration
- Consensual roleplay with informed partners
- Creative writing and storytelling
- Therapeutic self-improvement
- Educational research

### ❌ Prohibited Uses

- Non-consensual application to others
- Distribution without explicit consent
- Bypassing consent mechanisms
- Harmful or exploitative purposes
- Illegal activities

### Best Practices

1. **Always Test First**: Review generated scripts before use
2. **Start Conservative**: Begin with higher safety levels
3. **Document Consent**: Keep records of agreed-upon boundaries
4. **Include Safeguards**: Every script must have emergency exit
5. **Aftercare**: Plan for post-session grounding
6. **Storage**: Generated scripts are logged in `./hub/scripts/`
7. **Privacy**: Keep scripts private and secure

---

## Additional Resources

### Community Models

Explore more models at:
- [Ollama Model Library](https://ollama.com/library)
- [Hugging Face](https://huggingface.co/models)

### Script Templates

Check `./hub/scripts/` for examples of:
- Safe relaxation scripts (safety 5)
- Kink-friendly scripts (safety 2-3)
- Emergency procedures

### Documentation

- [README.md](README.md) - Project overview
- [SETUP.md](SETUP.md) - Installation guide
- [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md) - Ubuntu optimization

---

## Support

For issues with uncensored models:

1. Check Ollama is running: `ollama list`
2. Test model directly: `ollama run dolphin-llama3:8b "test"`
3. Check logs: `cat ./hub/logs/session.log`
4. Verify VRAM usage: `watch -n1 nvidia-smi` or `rocm-smi`

---

**Remember**: With great power comes great responsibility. Use uncensored models ethically and consensually. 🌀
