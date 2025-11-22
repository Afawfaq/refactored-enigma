# Hypno-Hub: Consensual Immersive Media System

## System Overview

Hypno-Hub is a **privacy-first, containerized platform** for creating and experiencing personalized, consensual hypnotic sessions. Designed for self-exploration and roleplay scenarios, it combines AI-generated content with synchronized multimedia playback in a fully isolated, offline environment. All processing occurs locally—no data leaves your machine.

### Core Philosophy

- **Explicit Consent First**: Sessions cannot begin without active user acknowledgment
- **Instant Escape**: Physical kill-switch (`Alt+Shift+E`) terminates all media immediately  
- **Complete Isolation**: Runs in an air-gapped Docker container with no network access
- **User Control**: All content is user-provided or AI-generated on-demand; no external dependencies

---

## Technical Architecture

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Web Interface** | Consent portal & session controller | Flask (Python) |
| **Video Engine** | Seamless looped video playback | `mpv` (hardware-accelerated) |
| **Image Engine** | Fullscreen slideshow overlay | `feh` (randomized, timed) |
| **Audio Engine** | Multi-layer audio mixing | `mpv` (binaural support) |
| **AI Core** | Dynamic script & trigger generation | Ollama (local LLM) |
| **Container** | Isolation & dependency management | Docker + Docker Compose |

### Data Flow

1. **User lands on consent page** (`http://localhost:9999`)
2. **Acknowledges safety terms** and submits preferences (persona, duration, themes)
3. **Ollama generates** a personalized script based on input
4. **Optional: Stable Diffusion** creates matching visuals (if enabled)
5. **mpv & feh** begin synchronized playback
6. **Session runs** until user triggers kill-switch or duration expires

---

## Safety Features

### Consent Gate
The HTML consent page requires explicit user action before any media loads. It displays:
- A clear statement of sobriety and awareness
- The physical kill-switch combination (`Alt+Shift+E`)
- A prominent "Enter" button that must be clicked

### Kill-Switch Mechanism
- **Global hotkey**: `Alt+Shift+E` sends `SIGTERM` to all media processes
- **i3 WM integration**: Exits the window manager, returning to login prompt (optional)
- **Manual stop**: Use the `/api/stop` endpoint or `docker-compose down`

### Air-Gapped Operation (Optional)
- **No network interfaces** in the Docker container (configure in docker-compose.yml)
- **ROCm GPU passthrough**: GPU remains isolated from host network stack
- **Media is local-only**: All video/image/audio files reside in `./hub/media/`

---

## Setup Instructions

### Prerequisites

**Required:**
- Docker 20.10+ and Docker Compose 2.0+
- Linux system (tested on Debian 12, Ubuntu 22.04) or Windows 10/11 with WSL2
- 4GB+ RAM, 10GB+ disk space
- Python 3 and pip (automatically installed by setup scripts)

**Optional (for GPU acceleration):**
- AMD GPU with ROCm support or NVIDIA GPU with CUDA
- Proxmox VE 8.x for VM deployment

**Optional (for AI features):**
- Ollama installed on host machine
- At least one LLM model pulled (e.g., `llama3.1:8b`)

**For Windows Users:**
- See [WINDOWS-SETUP.md](WINDOWS-SETUP.md) for detailed Windows installation instructions
- Docker Desktop for Windows with WSL2 backend recommended

### Automated Setup (Recommended)

> **📦 Need direct download links?** See [QUICK-INSTALL.md](QUICK-INSTALL.md) for all resource URLs.

**For Ubuntu (Native or WSL):**
```bash
# Clone the repository
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma

# Run automated setup (auto-installs Python 3, pip, git, Docker, and more)
# Works on both native Ubuntu and WSL Ubuntu
bash ubuntu-setup.sh

# Log out and back in for group membership, then start the service
docker compose up -d
```

**The ubuntu-setup.sh script automatically:**
- ✅ Detects if running in WSL or native Ubuntu
- ✅ Installs Python 3, pip, git, curl, wget (if missing)
- ✅ Installs Docker (native package for Ubuntu, or Docker Engine for WSL)
- ✅ Installs media libraries (mpv, feh, etc.)
- ✅ Installs ROCm for AMD GPUs (if detected and not in WSL)
- ✅ Creates all required directories
- ✅ Sets up environment configuration

**For Windows with WSL (Recommended):**
```powershell
# Run as Administrator - Auto-installs WSL Ubuntu and all dependencies
powershell -ExecutionPolicy Bypass -File windows-setup.ps1
```

**The windows-setup.ps1 script automatically:**
- ✅ Installs WSL with Ubuntu distribution (if not present)
- ✅ Installs Python 3 and git (via winget if available)
- ✅ Verifies Docker Desktop is installed
- ✅ Runs ubuntu-setup.sh inside WSL Ubuntu to complete setup
- ✅ Configures environment for WSL integration

**After Windows setup, you can run from WSL Ubuntu:**
```bash
# Open Ubuntu from Start menu
cd /mnt/c/Users/YourUsername/path/to/refactored-enigma
docker compose up -d
```

### Manual Install

```bash
# 1. Clone the repository
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma

# 2. Create media directories and add .gitkeep files
mkdir -p hub/media/{video,img,audio}
mkdir -p hub/scripts hub/logs
touch hub/media/video/.gitkeep
touch hub/media/img/.gitkeep
touch hub/media/audio/.gitkeep
touch hub/scripts/.gitkeep
touch hub/logs/.gitkeep

# 3. Build the Docker image
docker-compose build

# 4. Start the service
docker-compose up -d

# 5. Access the web interface
# Open http://localhost:9999 in your browser
```

### Ollama Setup (Optional - for AI script generation)

On the **host machine** (not inside Docker):

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull a recommended model
ollama pull llama3.1:8b

# Or for smaller systems:
ollama pull llama3.1:3b
```

The Docker container will automatically connect to Ollama on the host via `host.docker.internal:11434`.

---

## Media Management

### Directory Layout

Place your content in `./hub/media/`:

```
hub/media/
├── video/   # Looped video files (any format mpv supports)
├── img/     # Slideshow images (JPG/PNG)
└── audio/   # Binaural beats, voice tracks (MP3/FLAC)
```

### Supported Formats

- **Video**: MP4, MKV, WebM, AVI (hardware-accelerated via VA-API/VDPAU)
- **Images**: JPEG, PNG, BMP, GIF (static)
- **Audio**: MP3, FLAC, OGG, WAV (multi-channel supported)

### Adding Content

```bash
# Example: Add video files
cp /path/to/your/videos/*.mp4 hub/media/video/

# Example: Add images
cp /path/to/your/images/*.jpg hub/media/img/

# Example: Add audio
cp /path/to/your/audio/*.mp3 hub/media/audio/
```

**Note**: The `.gitignore` excludes media files from version control to keep the repository clean.

---

## Using the System

### Starting a Session

1. Navigate to `http://localhost:9999`
2. Read the consent page carefully
3. Click "I Consent - Enter" to start
4. The session will begin with synchronized media playback

### Stopping a Session

**Method 1: Kill-Switch (Recommended)**
- Press `Alt+Shift+E` (if configured in your window manager)

**Method 2: API Endpoint**
```bash
curl -X POST http://localhost:9999/api/stop
```

**Method 3: Docker Command**
```bash
docker-compose down
```

### Health Check

Check if the service is running:
```bash
curl http://localhost:9999/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "hypno-hub",
  "version": "1.0.0"
}
```

---

## AI Integration

### Generating Scripts

The `ai_llm.py` module provides AI-powered script generation using Ollama.

**Test the connection:**
```bash
docker-compose exec hypno-hub python3 /home/beta/hub/ai_llm.py
```

**Generate a custom script programmatically:**
```python
from ai_llm import OllamaClient

client = OllamaClient()

script = client.generate_script(
    persona="gentle guide",
    duration=20,
    themes=["relaxation", "positive affirmation", "mindfulness"],
    voice_style="calm and soothing"
)

print(script['script'])
```

**Script files** are saved in `./hub/scripts/` with timestamps:
- `script_YYYYMMDD_HHMMSS.txt` - Plain text version
- `script_YYYYMMDD_HHMMSS.json` - JSON with metadata

### Prompt Engineering

Modify the `_build_prompt()` method in `ai_llm.py` to customize script generation:

```python
def _build_prompt(self, persona, duration, themes, voice_style):
    # Add your custom prompt template here
    prompt = f"""Your custom instructions..."""
    return prompt
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Ollama configuration
OLLAMA_HOST=http://host.docker.internal:11434

# Display configuration (for X11 forwarding)
DISPLAY=:0

# Logging level
LOG_LEVEL=INFO
```

### Docker Compose Options

**Enable GPU acceleration (NVIDIA):**
```yaml
services:
  hypno-hub:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Enable GPU acceleration (AMD/ROCm):**
```yaml
services:
  hypno-hub:
    devices:
      - "/dev/kfd:/dev/kfd"
      - "/dev/dri:/dev/dri"
    group_add:
      - video
      - render
```

**Restrict network access (air-gapped mode):**
```yaml
services:
  hypno-hub:
    network_mode: "none"  # No network access
```

---

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

**Problem**: Dependency installation errors

**Solutions**:
```bash
# Clear Docker cache and rebuild
docker-compose build --no-cache

# Check Docker logs
docker-compose logs hypno-hub
```

#### 2. Cannot Access Web Interface

**Problem**: Port 9999 not accessible

**Solutions**:
```bash
# Check if service is running
docker-compose ps

# Check port binding
netstat -tulpn | grep 9999

# Try using host IP instead of localhost
curl http://127.0.0.1:9999
```

#### 3. Ollama Connection Failed

**Problem**: "Cannot connect to Ollama" error

**Solutions**:
```bash
# Verify Ollama is running on host
curl http://localhost:11434/api/tags

# Check Ollama service
systemctl status ollama  # if installed as service

# Test from inside container
docker-compose exec hypno-hub curl http://host.docker.internal:11434/api/tags
```

#### 4. No Media Playing

**Problem**: Black screen after starting session

**Solutions**:
```bash
# Check if media files exist
ls -lh hub/media/video/
ls -lh hub/media/img/

# Check session logs
docker-compose exec hypno-hub cat /home/beta/hub/logs/session.log

# Verify mpv installation
docker-compose exec hypno-hub mpv --version
```

#### 5. GPU Not Detected

**Problem**: Hardware acceleration not working

**Solutions**:
```bash
# Check GPU availability
docker-compose exec hypno-hub ls -l /dev/dri/

# Test GPU access
docker-compose exec hypno-hub vainfo  # for VA-API
docker-compose exec hypno-hub nvidia-smi  # for NVIDIA
```

#### 6. Permission Denied Errors

**Problem**: Cannot read/write files

**Solutions**:
```bash
# Fix ownership
sudo chown -R $USER:$USER hub/

# Fix permissions
chmod +x hub/start-hub.sh
chmod -R 755 hub/
```

### Viewing Logs

```bash
# Docker container logs
docker-compose logs -f hypno-hub

# Session logs
cat hub/logs/session.log

# Flask application logs
docker-compose exec hypno-hub tail -f /home/beta/hub/logs/session.log
```

---

## Security Considerations

### Data Privacy

- **Local Processing**: All AI generation happens locally via Ollama
- **No Telemetry**: No data is sent to external servers
- **Isolated Container**: Docker container has limited host access

### Safe Usage Guidelines

This tool is **only** for:
- ✅ Consenting adults exploring hypnotic experiences privately
- ✅ Self-hypnosis and personal development
- ✅ Roleplay scenarios with full pre-negotiation
- ✅ Educational purposes and research

**Absolutely not** for:
- ❌ Non-consensual application
- ❌ Distribution to unwitting parties
- ❌ Bypassing consent in any form
- ❌ Harmful or exploitative purposes

### Best Practices

1. **Always obtain explicit consent** before use
2. **Test the kill-switch** before each session
3. **Start with short durations** (5-10 minutes) initially
4. **Review generated content** before use
5. **Maintain awareness** of your mental state
6. **Have a trusted person available** if needed

---

## Development

### Project Structure

```
refactored-enigma/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore          # Build context exclusions
├── .gitignore             # Git exclusions
├── README.md              # Project overview
├── SETUP.md               # This file
└── hub/                   # Application directory
    ├── consent.html       # Consent page UI
    ├── launcher.py        # Flask web server
    ├── start-hub.sh       # Session management script
    ├── ai_llm.py          # Ollama integration
    ├── media/             # Media storage
    │   ├── video/         # Video files
    │   ├── img/           # Image files
    │   └── audio/         # Audio files
    ├── scripts/           # Generated scripts
    └── logs/              # Session logs
```

### Running in Development Mode

```bash
# Build with development settings
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Install additional Python packages
docker-compose exec hypno-hub pip install <package>

# Access container shell
docker-compose exec hypno-hub /bin/bash
```

### Testing

```bash
# Test Ollama connection
docker-compose exec hypno-hub python3 /home/beta/hub/ai_llm.py

# Test web interface
curl http://localhost:9999/health

# Test session start
curl -X POST http://localhost:9999/start

# Test session stop
curl -X POST http://localhost:9999/api/stop
```

---

## Contributing

This is a personal project focused on safety and consent. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Please ensure all contributions align with the ethical guidelines outlined above.

---

## Ethics & Responsibility

By using this software, you affirm that you will:

- **Prioritize safety and consent** in all usage
- **Respect the autonomy** of all participants
- **Use responsibly** and within legal boundaries
- **Not harm others** through misuse of this tool

If you witness or experience misuse of this software, please report it to appropriate authorities.

---

## Resources

### Related Projects

- **Ollama**: https://ollama.com/
- **MPV Player**: https://mpv.io/
- **Flask**: https://flask.palletsprojects.com/
- **Docker**: https://www.docker.com/

### Learning Resources

- **Hypnosis Safety**: Research ethical hypnosis practices
- **Docker Security**: https://docs.docker.com/engine/security/
- **Python Development**: https://docs.python.org/3/

---

## License

MIT License - See LICENSE file for details.

**Use responsibly and ethically.**

---

## Support

For issues, questions, or suggestions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include logs and error messages

**This project is provided as-is with no warranty. Use at your own risk.**
