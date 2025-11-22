# Hypno-Hub Windows Setup Guide

This guide provides step-by-step instructions for setting up Hypno-Hub on Windows systems.

## 🖥️ Windows Compatibility Notes

Hypno-Hub was originally designed for Linux systems but can run on Windows in several ways:

1. **Docker Desktop with WSL2** (Recommended) - Best compatibility and performance
2. **Docker Desktop on Windows** (Limited) - Web interface only, no GUI media playback
3. **Native WSL2 Installation** - Full Linux experience on Windows

**Important:** The application runs inside a Linux Docker container on all platforms. The Windows-specific setup scripts (`windows-setup.ps1`) are used only for initial setup on the Windows host. Once running, the container uses Linux tools (bash, mpv, feh) regardless of the host OS.

## Prerequisites

### Required Software

- **Windows 10/11** (64-bit) with latest updates
- **Docker Desktop for Windows** 4.0+ with WSL2 backend
- **4GB+ RAM** available for Docker
- **10GB+ disk space**

### Optional Software

- **Ollama for Windows** - For AI script generation features
- **WSL2** - For better Linux compatibility (recommended)

## Installation Methods

### Method 1: Docker Desktop with WSL2 (Recommended)

This method provides the best compatibility and allows full GUI functionality.

#### Step 1: Install WSL2

1. Open PowerShell as Administrator and run:
```powershell
wsl --install
```

2. Restart your computer when prompted

3. After restart, set up your Linux username and password

4. Update WSL2:
```powershell
wsl --update
```

#### Step 2: Install Docker Desktop

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop

2. Run the installer and select "Use WSL2 instead of Hyper-V" option

3. After installation, open Docker Desktop

4. Go to Settings → General → Enable "Use the WSL2 based engine"

5. Go to Settings → Resources → WSL Integration
   - Enable integration with your default WSL2 distro
   - Apply & Restart

#### Step 3: Install Hypno-Hub in WSL2

1. Open WSL2 terminal (search for "Ubuntu" or your installed distro in Start menu)

2. Clone the repository:
```bash
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma
```

3. Create required directories:
```bash
mkdir -p hub/media/{video,img,audio} hub/scripts hub/logs
```

4. Copy environment template:
```bash
cp .env.example .env
```

5. Build and start the service:
```bash
docker compose up -d
```

6. Access the interface at: http://localhost:9999

### Method 2: Native Windows Docker (Web Only)

This method runs the web interface but GUI media playback won't work natively.

#### Step 1: Install Docker Desktop

Follow steps 1-3 from Method 1 above (Docker Desktop installation).

#### Step 2: Install Hypno-Hub

1. Open PowerShell and clone the repository:
```powershell
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma
```

2. Run the automated setup script **as Administrator**:
```powershell
# Right-click PowerShell and select "Run as Administrator", then run:
powershell -ExecutionPolicy Bypass -File windows-setup.ps1
```

**The setup script automatically installs (when run as Administrator):**
- **Windows Package Manager (winget)** - Checked for availability
- **Python 3 and pip** - Auto-installed via winget if missing
- **git** - Auto-installed via winget if missing
- **Docker Desktop and Docker Compose** - Checked (manual installation required if missing)
- Creates directory structure and environment files

**Note:** If not running as Administrator, the script will provide manual installation guidance with download links instead of auto-installing.

3. Or manually set up:
```powershell
# Create directories
New-Item -ItemType Directory -Path hub\media\video,hub\media\img,hub\media\audio,hub\scripts,hub\logs -Force

# Copy environment file
Copy-Item .env.example .env

# Build and start
docker compose -f docker-compose.windows.yml up -d
```

4. Access the interface at: http://localhost:9999

**Note:** Media playback runs inside the container. For GUI display, use Method 1 (WSL2).

## Adding Media Files

### Using Windows Explorer

1. Navigate to your cloned repository folder
2. Open `hub\media\`
3. Add your files to the appropriate folders:
   - `video\` - MP4, MKV, WebM, AVI files
   - `img\` - JPG, PNG, GIF files
   - `audio\` - MP3, FLAC, WAV files

### Using WSL2

If using Method 1, you can access Windows files from WSL2:
```bash
# Your Windows C: drive is at /mnt/c/
# Example: Copy files from Windows Downloads
cp /mnt/c/Users/YourUsername/Downloads/*.mp4 hub/media/video/
```

## Setting Up Ollama (Optional)

Ollama enables AI-generated hypnotic scripts.

### On Windows

1. Download Ollama for Windows: https://ollama.ai/download/windows

2. Install and run Ollama

3. Open PowerShell and pull a model:
```powershell
ollama pull llama3.1:8b
```

4. Ollama will run at `http://localhost:11434` (automatically detected)

### On WSL2

1. In WSL2 terminal:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:8b
```

## Usage

### Starting the Service

**WSL2:**
```bash
cd refactored-enigma
docker compose up -d
```

**Windows:**
```powershell
cd refactored-enigma
docker compose -f docker-compose.windows.yml up -d
```

### Accessing the Interface

Open your browser to: http://localhost:9999

1. Read and acknowledge the consent page
2. Click "I Consent - Enter"
3. Configure your session (if AI features enabled)
4. Session begins

### Stopping the Service

**WSL2:**
```bash
docker compose down
```

**Windows:**
```powershell
docker compose -f docker-compose.windows.yml down
```

Or use the API:
```powershell
curl -X POST http://localhost:9999/api/stop
```

## Troubleshooting

### Docker Desktop Issues

**Problem:** "Docker Desktop is not running"
```powershell
# Solution: Start Docker Desktop from Start menu
# Wait for "Docker Desktop is running" in system tray
```

**Problem:** "WSL2 installation is incomplete"
```powershell
# Solution: Update WSL2
wsl --update
# Restart Docker Desktop
```

### Service Won't Start

```powershell
# Check Docker status
docker ps

# View logs
docker logs hypno-hub

# Rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Port 9999 Already in Use

```powershell
# Find what's using the port
netstat -ano | findstr :9999

# Kill the process (replace PID with actual process ID)
taskkill /F /PID <PID>
```

### Ollama Connection Issues

```powershell
# Test Ollama connection
curl http://localhost:11434/api/tags

# If using WSL2, ensure Ollama is running
wsl -d Ubuntu -- pgrep ollama
```

### Media Files Not Playing

**On Native Windows Docker:**
- Media playback requires Linux GUI tools (mpv, feh)
- These run inside the container but need X11 forwarding
- **Solution:** Use WSL2 (Method 1) for full functionality

**On WSL2:**
```bash
# Check if files exist
ls -la hub/media/video/

# Check container logs
docker compose logs -f hypno-hub

# Verify file permissions
chmod 644 hub/media/video/*
```

## Performance Optimization

### Docker Desktop Settings

1. Open Docker Desktop → Settings → Resources

2. Recommended settings:
   - **CPUs:** 4+ cores
   - **Memory:** 4GB minimum, 8GB recommended
   - **Disk:** 20GB+

3. For WSL2, also configure in `.wslconfig`:
```ini
# Create/edit: C:\Users\YourUsername\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=2GB
```

### File System Performance

- Store repository on WSL2 filesystem for better performance
- Avoid placing it on `/mnt/c/` (Windows drives)
- Use native WSL2 home directory: `~/refactored-enigma`

## Security Considerations

### Windows Firewall

Docker Desktop automatically configures firewall rules. If you have issues:

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Ensure "Docker Desktop" is checked for both Private and Public networks

### Antivirus Software

Some antivirus software may interfere with Docker:
- Add Docker Desktop to exclusions
- Add WSL2 to exclusions if using Method 1

## Differences from Linux

| Feature | Linux | Windows (Native) | Windows (WSL2) |
|---------|-------|------------------|----------------|
| Web Interface | ✅ Full | ✅ Full | ✅ Full |
| Media Playback | ✅ Full | ⚠️ Container Only | ✅ Full |
| GPU Acceleration | ✅ Yes | ❌ Limited | ⚠️ Limited |
| Kill-Switch | ✅ i3 WM | ❌ No | ⚠️ Partial |
| Performance | ✅ Native | ⚠️ Good | ✅ Near-Native |
| Setup Complexity | ⚠️ Medium | ✅ Easy | ⚠️ Medium |

## Recommended Setup

For the best Windows experience:

1. **Use WSL2 with Docker Desktop** (Method 1)
2. Store repository in WSL2 filesystem (`~/refactored-enigma`)
3. Install Ollama in WSL2 for AI features
4. Use Windows Terminal for better WSL2 experience
5. Consider using VcXsrv or X410 for X11 forwarding if needed

## Getting Help

- **Documentation:** See main [README.md](README.md) and [SETUP.md](SETUP.md)
- **WSL2 Issues:** https://docs.microsoft.com/windows/wsl/troubleshooting
- **Docker Desktop Issues:** https://docs.docker.com/desktop/troubleshooting/overview/
- **GitHub Issues:** https://github.com/Afawfaq/refactored-enigma/issues

## Additional Resources

- **Docker Desktop for Windows:** https://docs.docker.com/desktop/install/windows-install/
- **WSL2 Setup:** https://docs.microsoft.com/windows/wsl/install
- **Ollama for Windows:** https://ollama.ai/download/windows
- **Windows Terminal:** https://aka.ms/terminal

---

**Note:** While Hypno-Hub can run on Windows, it's optimized for Linux. For production use or the best experience, consider using a dedicated Ubuntu installation or VM.
