# Quick Installation Resources

This guide provides direct links to all required resources for manual installation.

## 🚀 For Windows Users (WSL Ubuntu Recommended)

### Step 1: Install WSL with Ubuntu

**Option A: Automatic (PowerShell as Administrator)**
```powershell
wsl --install -d Ubuntu
```

**Option B: Manual Download**
- **WSL Documentation**: https://docs.microsoft.com/windows/wsl/install
- **Ubuntu from Microsoft Store**: https://www.microsoft.com/store/productId/9PDXGNCFSCZV

### Step 2: Install Docker Desktop

**Docker Desktop for Windows**
- **Download**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- **Official Page**: https://www.docker.com/products/docker-desktop/
- **Documentation**: https://docs.docker.com/desktop/install/windows-install/

**Note**: Enable WSL2 integration in Docker Desktop settings after installation.

### Step 3: Install Windows Package Manager (Optional but Recommended)

**Windows Package Manager (winget)**
- **App Installer from Microsoft Store**: https://www.microsoft.com/store/productId/9NBLGGH4NNS1
- **Documentation**: https://learn.microsoft.com/windows/package-manager/winget/

### Step 4: Install Python (if needed on Windows)

**Python 3.12+**
- **Download**: https://www.python.org/downloads/
- **Direct Link (3.12)**: https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
- **Documentation**: https://docs.python.org/3/using/windows.html

**Important**: Check "Add Python to PATH" during installation.

### Step 5: Install Git (if needed on Windows)

**Git for Windows**
- **Download**: https://git-scm.com/download/win
- **Direct Link**: https://github.com/git-for-windows/git/releases/latest
- **Documentation**: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

---

## 🐧 For Linux/Ubuntu Users (Native or WSL)

### Essential Dependencies

**Python 3 and pip**
```bash
sudo apt update
sudo apt install -y python3 python3-pip
```
- **Python Official**: https://www.python.org/downloads/
- **pip Documentation**: https://pip.pypa.io/en/stable/installation/

**Git**
```bash
sudo apt install -y git
```
- **Git Downloads**: https://git-scm.com/downloads
- **Git Documentation**: https://git-scm.com/doc

**curl and wget**
```bash
sudo apt install -y curl wget
```

### Docker Installation

**For Ubuntu (Native)**
```bash
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```
- **Docker Official Docs**: https://docs.docker.com/engine/install/ubuntu/
- **Docker Compose Plugin**: https://docs.docker.com/compose/install/linux/

**For WSL Ubuntu (with Docker Desktop)**
- Use Docker Desktop from Windows (see above)
- Enable WSL integration in Docker Desktop settings

**For WSL Ubuntu (Native Docker Engine)**
```bash
# Add Docker's official repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
- **Docker Engine on Ubuntu**: https://docs.docker.com/engine/install/ubuntu/

### Media Libraries

```bash
sudo apt install -y mpv feh libmpv2 libdrm-amdgpu1 mesa-vulkan-drivers vainfo
```

**Individual Downloads:**
- **mpv**: https://mpv.io/installation/
- **feh**: https://feh.finalrewind.org/
- **Mesa**: https://www.mesa3d.org/

---

## 🤖 Optional: AI Features (Ollama)

### For Windows

**Ollama for Windows**
- **Download**: https://ollama.com/download/windows
- **Latest Release**: https://github.com/ollama/ollama/releases/latest
- **Documentation**: https://github.com/ollama/ollama

### For Linux/Ubuntu/WSL

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Manual Download:**
- **Ollama Download Page**: https://ollama.com/download
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Ollama Documentation**: https://github.com/ollama/ollama/blob/main/README.md

**After Installation:**
```bash
# Start Ollama
ollama serve &

# Pull a model
ollama pull llama3.1:8b
```

**Model Library**: https://ollama.com/library

---

## 🎮 Optional: GPU Support

### For AMD GPUs (ROCm)

**ROCm 6.2+ Installation**
```bash
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.2/ ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install -y rocm-hip-sdk rocminfo
sudo usermod -aG render,video $USER
```

**Resources:**
- **ROCm Documentation**: https://rocm.docs.amd.com/
- **ROCm Installation Guide**: https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html
- **ROCm Downloads**: https://repo.radeon.com/rocm/

### For NVIDIA GPUs (CUDA)

**NVIDIA CUDA Toolkit**
- **CUDA Downloads**: https://developer.nvidia.com/cuda-downloads
- **CUDA Documentation**: https://docs.nvidia.com/cuda/
- **cuDNN**: https://developer.nvidia.com/cudnn

---

## 📦 Project Setup

### Clone Repository

```bash
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma
```

**Repository**: https://github.com/Afawfaq/refactored-enigma

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- **Flask**: https://flask.palletsprojects.com/
- **Requests**: https://requests.readthedocs.io/

### Create Directory Structure

```bash
mkdir -p hub/media/{video,img,audio} hub/scripts hub/logs
touch hub/media/{video,img,audio}/.gitkeep
touch hub/{scripts,logs}/.gitkeep
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Build and Start

```bash
# Build Docker image
docker compose build

# Start service
docker compose up -d

# Access interface
# Open http://localhost:9999 in your browser
```

---

## 🔧 Additional Tools

### Terminal Emulators

**Windows Terminal (Recommended for WSL)**
- **Microsoft Store**: https://www.microsoft.com/store/productId/9N0DX20HK701
- **GitHub**: https://github.com/microsoft/terminal

### X Server for WSL (for GUI applications)

**VcXsrv**
- **Download**: https://sourceforge.net/projects/vcxsrv/
- **Documentation**: https://sourceforge.net/p/vcxsrv/wiki/Home/

**X410 (Paid)**
- **Microsoft Store**: https://www.microsoft.com/store/productId/9NLP712ZMN9Q

### Code Editors

**Visual Studio Code**
- **Download**: https://code.visualstudio.com/download
- **WSL Extension**: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl

---

## 📚 Documentation Resources

### Official Documentation
- **Project README**: [README.md](README.md)
- **Full Setup Guide**: [SETUP.md](SETUP.md)
- **Windows Setup Guide**: [WINDOWS-SETUP.md](WINDOWS-SETUP.md)
- **Ubuntu 25.04 Guide**: [UBUNTU-25.04-SETUP.md](UBUNTU-25.04-SETUP.md)
- **Testing Guide**: [TESTING.md](TESTING.md)

### External Resources
- **Docker Documentation**: https://docs.docker.com/
- **WSL Documentation**: https://docs.microsoft.com/windows/wsl/
- **Ubuntu Documentation**: https://help.ubuntu.com/
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## ⚡ Automated Setup Scripts

Instead of manual installation, you can use our automated setup scripts:

### Windows (PowerShell as Administrator)
```powershell
powershell -ExecutionPolicy Bypass -File windows-setup.ps1
```
**This auto-installs:** WSL, Ubuntu, Docker Desktop, Python, Git, and runs ubuntu-setup.sh

### Ubuntu/WSL Ubuntu
```bash
bash ubuntu-setup.sh
```
**This auto-installs:** Python, pip, git, curl, wget, Docker, media libraries, and ROCm (if AMD GPU detected)

---

## 🆘 Support Resources

- **GitHub Issues**: https://github.com/Afawfaq/refactored-enigma/issues
- **Docker Community**: https://forums.docker.com/
- **WSL GitHub**: https://github.com/microsoft/WSL
- **Ubuntu Forums**: https://ubuntuforums.org/

---

## ✅ Quick Verification

After installation, verify everything is working:

```bash
# Check Python
python3 --version

# Check pip
pip3 --version

# Check Git
git --version

# Check Docker
docker --version
docker compose version

# Check Ollama (if installed)
ollama --version

# Run project validation
python validate.py
```

---

**All links current as of November 2024. Always download from official sources.**
