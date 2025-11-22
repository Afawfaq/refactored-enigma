# Hypno-Hub API Documentation

This document describes the HTTP API endpoints available in Hypno-Hub.

## Base URL

```
http://localhost:9999
```

## Endpoints

### Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "hypno-hub",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:9999/health
```

---

### Consent Page

Display the consent and safety information page.

**Endpoint:** `GET /`

**Response:** HTML page with consent form

**Example:**
```bash
curl http://localhost:9999/
```

---

### Configuration Page

Display the persona and kink zone configuration page.

**Endpoint:** `GET /configure`

**Response:** HTML page with configuration form

**Example:**
```bash
curl http://localhost:9999/configure
```

---

### Configure Session

Submit configuration and generate AI script.

**Endpoint:** `POST /configure`

**Parameters:**
- `persona` (string, optional) - Persona key (default: "gentle_guide")
  - Valid values: gentle_guide, gentle_domme, strict_hypnotist, sleep_specialist, fantasy_guide, bimbo_coach, therapist, custom
- `kink_zone` (string, optional) - Comma-separated kink zone keys (default: "relaxation")
  - Valid values: relaxation, submission, transformation, triggers, sensory, fantasy, sleep, confidence
- `model` (string, optional) - Ollama model name (default: "dolphin-llama3:8b")
- `safety_level` (integer, optional) - Safety level 1-5 (default: 3)
  - 1: Minimal guardrails
  - 2: Low guardrails
  - 3: Medium guardrails (default)
  - 4: High guardrails
  - 5: Maximum guardrails
- `duration` (integer, optional) - Duration in minutes, 5-120 (default: 20)

**Response:** Redirect to `/start_configured`

**Example:**
```bash
curl -X POST http://localhost:9999/configure \
  -d "persona=gentle_domme" \
  -d "kink_zone=submission" \
  -d "model=dolphin-llama3:8b" \
  -d "safety_level=3" \
  -d "duration=25"
```

---

### Start Session

Start a hypnosis session after consent.

**Endpoint:** `POST /start`

**Response:** Redirect to `/session`

**Example:**
```bash
curl -X POST http://localhost:9999/start
```

---

### Session Status

Display active session page.

**Endpoint:** `GET /session`

**Response:** HTML page showing session is active

**Example:**
```bash
curl http://localhost:9999/session
```

---

### Stop Session

Stop all media playback and end the session.

**Endpoint:** `POST /api/stop`

**Response:**
```json
{
  "status": "stopped"
}
```

**Example:**
```bash
curl -X POST http://localhost:9999/api/stop
```

---

### List Personas

Get all available personas.

**Endpoint:** `GET /api/personas`

**Response:**
```json
[
  {
    "key": "gentle_guide",
    "name": "Gentle Guide",
    "description": "Soft-spoken, reassuring, nurturing presence",
    "safety_level": 5,
    "model": "llama3.1:8b"
  },
  {
    "key": "gentle_domme",
    "name": "Gentle Domme",
    "description": "Caring but authoritative, gentle dominance",
    "safety_level": 4,
    "model": "dolphin-llama3:8b"
  }
]
```

**Example:**
```bash
curl http://localhost:9999/api/personas
```

---

### List Kink Zones

Get all available kink zones/themes.

**Endpoint:** `GET /api/kink-zones`

**Response:**
```json
[
  {
    "key": "relaxation",
    "name": "Relaxation & Mindfulness",
    "description": "Pure relaxation and mental wellness",
    "safety_level": 5,
    "themes": ["deep relaxation", "meditation", "stress relief", "mindfulness"]
  },
  {
    "key": "submission",
    "name": "Submission & Obedience",
    "description": "Power exchange and control themes",
    "safety_level": 3,
    "themes": ["obedience", "submission", "surrender", "compliance"]
  }
]
```

**Example:**
```bash
curl http://localhost:9999/api/kink-zones
```

---

### List Models

Get information about available AI models.

**Endpoint:** `GET /api/models`

**Response:**
```json
[
  {
    "name": "dolphin-llama3:8b",
    "size": "4.7 GB",
    "vram": "5.2 GB",
    "speed": "fast",
    "best_for": "Creative roleplay, triggers, immersive scenarios"
  },
  {
    "name": "llama3.1:8b",
    "size": "4.7 GB",
    "vram": "5.2 GB",
    "speed": "fast",
    "best_for": "General purpose, censored"
  }
]
```

**Example:**
```bash
curl http://localhost:9999/api/models
```

---

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK` - Request successful
- `302 Found` - Redirect (after form submission)
- `500 Internal Server Error` - Server error

Error responses include a message:
```json
{
  "error": "Error description here"
}
```

Or as plain text:
```
Error: Error description here
```

## Safety Features

### Input Validation

The API validates all inputs:
- Safety level must be 1-5 (defaults to 3)
- Duration must be 5-120 minutes (defaults to 20)
- Invalid values are logged and defaults are used

### Emergency Stop

The `/api/stop` endpoint can be called at any time to immediately stop all media playback:

```bash
# Stop session from command line
curl -X POST http://localhost:9999/api/stop

# Or integrate with keyboard shortcuts (e.g., i3 config)
bindsym $mod+Shift+e exec "curl -X POST http://localhost:9999/api/stop"
```

## Integration Examples

### Python

```python
import requests

# Health check
response = requests.get("http://localhost:9999/health")
print(response.json())

# Get personas
personas = requests.get("http://localhost:9999/api/personas").json()
for persona in personas:
    print(f"{persona['name']}: {persona['description']}")

# Configure session
data = {
    "persona": "gentle_domme",
    "kink_zone": "submission",
    "model": "dolphin-llama3:8b",
    "safety_level": 3,
    "duration": 20
}
response = requests.post("http://localhost:9999/configure", data=data)

# Stop session
requests.post("http://localhost:9999/api/stop")
```

### JavaScript

```javascript
// Health check
fetch('http://localhost:9999/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Get kink zones
fetch('http://localhost:9999/api/kink-zones')
  .then(response => response.json())
  .then(zones => {
    zones.forEach(zone => {
      console.log(`${zone.name}: ${zone.description}`);
    });
  });

// Stop session
fetch('http://localhost:9999/api/stop', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Bash

```bash
#!/bin/bash

# Health check
curl -s http://localhost:9999/health | jq .

# List personas
curl -s http://localhost:9999/api/personas | jq '.[] | {name, safety_level}'

# Configure and start session
curl -X POST http://localhost:9999/configure \
  -d "persona=gentle_guide" \
  -d "duration=15" \
  -d "safety_level=5"

# Wait for session
sleep 900  # 15 minutes

# Stop session
curl -X POST http://localhost:9999/api/stop
```

## Rate Limiting

There is currently no rate limiting implemented. The API is designed for local, single-user use.

## Authentication

There is no authentication. The service is designed to run locally in a trusted environment.

**Security Note:** Do not expose this service to the internet without adding authentication and HTTPS.

## CORS

CORS is not explicitly configured. The service is designed for same-origin requests from the web UI.

## WebSocket Support

The current version does not support WebSockets. All communication is HTTP-based.

## Future API Endpoints

Potential future endpoints (not yet implemented):
- `GET /api/scripts` - List generated scripts
- `GET /api/scripts/:id` - Get specific script
- `DELETE /api/scripts/:id` - Delete a script
- `GET /api/session/status` - Get current session status
- `PUT /api/session/pause` - Pause current session
- `PUT /api/session/resume` - Resume paused session

## Troubleshooting

### Connection Refused

```bash
# Check if service is running
docker compose ps

# Start service if stopped
docker compose up -d

# Check logs
docker compose logs -f hypno-hub
```

### 500 Internal Server Error

```bash
# Check logs for details
docker compose logs hypno-hub | tail -50

# Common issues:
# - Ollama not running: Start with `ollama serve`
# - Missing media files: Add files to hub/media/
# - Script not found: Check hub/start-hub.sh exists and is executable
```

### No Response from API

```bash
# Test connectivity
curl -v http://localhost:9999/health

# Check if port is bound
sudo netstat -tlnp | grep 9999

# Check Docker port mapping
docker compose port hypno-hub 9999
```

## Support

For API issues or questions:
- Check logs: `docker compose logs hypno-hub`
- Review documentation: [README.md](README.md), [SETUP.md](SETUP.md)
- Open issue: [GitHub Issues](https://github.com/Afawfaq/refactored-enigma/issues)
