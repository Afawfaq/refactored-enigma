# Hypno-Hub: Consensual Immersive Media System

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Python](https://img.shields.io/badge/python-3.13-brightgreen)
![Ubuntu](https://img.shields.io/badge/ubuntu-25.04%20optimized-orange)

A **privacy-first, containerized platform** for creating and experiencing personalized, consensual hypnotic sessions. Combines AI-generated content with synchronized multimedia playback in a fully isolated, offline environment.

> **🎯 Optimized for Ubuntu 25.04 "Plucky Puffin"** - See [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md) for detailed Ubuntu 25.04 installation and optimization guide.

## 🌟 Features

- **🔒 Consent-First Design**: Explicit consent gate before any session begins
- **🚨 Emergency Kill-Switch**: Instant termination with `Alt+Shift+E`
- **🤖 AI-Powered Scripts**: Integration with Ollama for dynamic content generation
- **🎬 Synchronized Media**: Video, images, and audio playback in harmony
- **🐳 Fully Containerized**: Easy deployment with Docker Compose
- **🔐 Privacy-Focused**: All processing happens locally, no data leaves your machine
- **⚡ Hardware Accelerated**: GPU support for smooth video playback (AMD 7800 XT optimized)
- **🐧 Ubuntu 25.04 Optimized**: Kernel 6.14, Python 3.13, ROCm 6.2+, Docker 28+

## ⚠️ Safety & Ethics

This tool is designed for **consenting adults** exploring hypnotic experiences privately. 

### ✅ Appropriate Uses:
- Self-hypnosis and personal development
- Consensual roleplay scenarios
- Educational purposes and research
- Private exploration of hypnotic techniques

### ❌ Inappropriate Uses:
- Non-consensual application
- Distribution to unwitting parties
- Bypassing consent in any form
- Harmful or exploitative purposes

**By using this software, you agree to prioritize safety, consent, and ethical use.**

## 🚀 Quick Start

### For Ubuntu 25.04 Users (Recommended)

```bash
# Clone the repository
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma

# Run automated setup
bash ubuntu-setup.sh

# Log out and back in for group membership
# Then start the service
docker compose up -d

# Access at http://localhost:9999
```

**📖 See [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md) for complete Ubuntu 25.04 guide including:**
- ROCm 6.2+ installation for AMD GPUs
- GPU support configuration
- Kernel 6.14 optimization
- Advanced troubleshooting

### For Other Linux Distributions

#### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Linux system with kernel 5.10+ (6.14+ recommended for AMD GPUs)
- 4GB+ RAM, 10GB+ disk space
- **Optional**: Ollama for AI features
- **Optional**: GPU for hardware acceleration

#### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma

# 2. Create required directories
mkdir -p hub/media/{video,img,audio} hub/scripts hub/logs

# 3. Copy environment template
cp .env.example .env

# 4. Build and start
docker compose up -d

# 5. Access the interface
# Open http://localhost:9999 in your browser
```

### With Ollama (AI Features)

```bash
# On host machine:
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:8b

# The Docker container will automatically connect to Ollama
```

## 📖 Documentation

- **[Ubuntu 25.04 Setup Guide](UBUNTU-25.04-SETUP.md)** - Comprehensive Ubuntu 25.04 installation, GPU passthrough, and optimization
- **[Complete Setup Guide](SETUP.md)** - Detailed installation and configuration for all platforms
- **Architecture** - See SETUP.md for technical details
- **Troubleshooting** - Platform-specific guides in respective documentation

## 🎯 Usage

### Starting a Session

1. Navigate to `http://localhost:9999`
2. Read and acknowledge the consent page
3. Click "I Consent - Enter"
4. Session begins with synchronized media

### Stopping a Session

- **Kill-Switch**: Press `Alt+Shift+E` (if configured in i3 WM)
- **API**: `curl -X POST http://localhost:9999/api/stop`
- **Docker**: `docker compose down`

### Adding Media

```bash
# Add your content to these directories:
hub/media/video/  # Video files (MP4, MKV, WebM, etc.)
hub/media/img/    # Images (JPG, PNG, etc.)
hub/media/audio/  # Audio files (MP3, FLAC, etc.)
```

## 🏗️ Architecture

```
┌─────────────────┐
│  Web Browser    │  (Consent UI @ :9999)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Server   │  (launcher.py)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌─────┐  ┌────────┐ ┌──────────┐
│  MPV   │ │ Feh │  │  MPV   │ │  Ollama  │
│ Video  │ │Image│  │ Audio  │ │   (AI)   │
│(GPU HW)│ │Show │  │ Layer  │ │  (Host)  │
└────────┘ └─────┘  └────────┘ └──────────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
              │
         User Experience
```

## 🛠️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Display configuration
DISPLAY=:0
GDK_BACKEND=x11

# Ollama configuration
OLLAMA_HOST=http://host.docker.internal:11434

# AMD GPU configuration (7800 XT / RDNA 3)
HSA_OVERRIDE_GFX_VERSION=11.0.0
ROCR_VISIBLE_DEVICES=0

# Logging
LOG_LEVEL=INFO
```

### GPU Acceleration

**NVIDIA:**
```yaml
# Add to docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

**AMD (Ubuntu 25.04 Optimized):**
```yaml
# Already configured in docker-compose.yml
devices:
  - "/dev/kfd:/dev/kfd"
  - "/dev/dri:/dev/dri"
environment:
  - HSA_OVERRIDE_GFX_VERSION=11.0.0
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:9999/health

# Test Ollama connection
docker compose exec hypno-hub python3 /home/beta/hub/ai_llm.py

# View logs
docker compose logs -f hypno-hub

# Check GPU access
docker compose exec hypno-hub ls -l /dev/dri
```

## 📂 Project Structure

```
refactored-enigma/
├── Dockerfile                    # Ubuntu 25.04 optimized container
├── docker-compose.yml            # Service orchestration with GPU support
├── README.md                     # This file
├── SETUP.md                      # General setup guide
├── UBUNTU-25.04-SETUP.md        # Ubuntu 25.04 specific guide
├── ubuntu-setup.sh               # Automated Ubuntu 25.04 setup
├── .env.example                  # Environment configuration template
├── config/                       # System configuration files
│   ├── sysctl-hypno-hub.conf    # Kernel tuning for Ubuntu 25.04
│   └── i3-config-snippet.conf   # Kill-switch configuration
└── hub/                          # Application
    ├── consent.html              # Consent UI
    ├── launcher.py               # Flask web server
    ├── start-hub.sh              # Session manager
    ├── ai_llm.py                 # Ollama integration
    ├── media/                    # Content storage
    │   ├── video/
    │   ├── img/
    │   └── audio/
    ├── scripts/                  # Generated AI scripts
    └── logs/                     # Session logs
```

## 🐛 Troubleshooting

### Quick Diagnostics

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f hypno-hub

# Test Ollama
curl http://localhost:11434/api/tags

# Check GPU (AMD)
lspci | grep -i amd
/opt/rocm/bin/rocminfo
```

### Common Issues

**Service won't start:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**No media playing:**
```bash
ls -lh hub/media/video/  # Ensure files exist
cat hub/logs/session.log  # Check session logs
```

**Ollama not connecting:**
```bash
# From container
docker compose exec hypno-hub curl http://host.docker.internal:11434/api/tags
```

**Ubuntu 25.04 Specific Issues:**
- See [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md) for detailed troubleshooting

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (especially on Ubuntu 25.04)
5. Submit a pull request

Ensure all contributions align with our ethical guidelines.

## 📜 License

MIT License - see LICENSE file for details.

**Use responsibly and ethically. Prioritize consent and safety.**

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **MPV** - Media playback
- **Flask** - Web framework
- **Docker** - Containerization
- **Ubuntu** - Operating system
- **ROCm** - AMD GPU compute stack

## 📞 Support

- **Ubuntu 25.04 Guide**: [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md)
- **General Documentation**: [SETUP.md](SETUP.md)
- **Issues**: [GitHub Issues](https://github.com/Afawfaq/refactored-enigma/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Afawfaq/refactored-enigma/discussions)

### System Information for Bug Reports

```bash
# Include this information when reporting issues:
lsb_release -a          # Ubuntu version
uname -r                # Kernel version
docker --version        # Docker version
lspci | grep -i vga     # GPU information
/opt/rocm/bin/rocminfo  # ROCm information (if AMD GPU)
```

---

**⚠️ Important**: This software is provided as-is with no warranty. Users are responsible for ensuring ethical and legal use. Always prioritize consent, safety, and respect for autonomy.

**🎯 For the best experience, use Ubuntu 25.04 "Plucky Puffin" with the optimized setup guide.**
