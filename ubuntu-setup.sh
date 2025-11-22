#!/bin/bash
#
# Ubuntu Setup Script for Hypno-Hub (Native Ubuntu & WSL)
# Run with: bash ubuntu-setup.sh
#
# This script auto-installs all dependencies for both native Ubuntu and WSL Ubuntu environments
#

set -e

echo "=== Hypno-Hub Ubuntu Setup ==="
echo ""

# Detect WSL environment
IS_WSL=false
if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
    IS_WSL=true
    echo "✓ WSL Ubuntu environment detected"
    echo ""
elif grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
    IS_WSL=true
    echo "✓ WSL Ubuntu environment detected"
    echo ""
else
    echo "✓ Native Ubuntu environment detected"
    echo ""
fi

# Check Ubuntu version (allow any version, just warn if not 25.04)
if ! grep -q "25.04" /etc/os-release 2>/dev/null; then
    echo "Note: This script is optimized for Ubuntu 25.04 but will work on other versions"
    if [ "$IS_WSL" = false ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "Continuing with WSL Ubuntu setup..."
    fi
    echo ""
fi

# Install essential dependencies (Python, git, curl, wget)
echo "[1/9] Checking and installing essential dependencies..."
ESSENTIAL_PACKAGES=""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "  - Python 3 not found, will install"
    ESSENTIAL_PACKAGES="$ESSENTIAL_PACKAGES python3"
else
    echo "  - Python 3 already installed: $(python3 --version)"
fi

# Check for pip3
if ! command -v pip3 &> /dev/null; then
    echo "  - pip3 not found, will install"
    ESSENTIAL_PACKAGES="$ESSENTIAL_PACKAGES python3-pip"
else
    echo "  - pip3 already installed: $(pip3 --version)"
fi

# Check for git
if ! command -v git &> /dev/null; then
    echo "  - git not found, will install"
    ESSENTIAL_PACKAGES="$ESSENTIAL_PACKAGES git"
else
    echo "  - git already installed: $(git --version)"
fi

# Check for curl
if ! command -v curl &> /dev/null; then
    echo "  - curl not found, will install"
    ESSENTIAL_PACKAGES="$ESSENTIAL_PACKAGES curl"
else
    echo "  - curl already installed"
fi

# Check for wget
if ! command -v wget &> /dev/null; then
    echo "  - wget not found, will install"
    ESSENTIAL_PACKAGES="$ESSENTIAL_PACKAGES wget"
else
    echo "  - wget already installed"
fi

# Install missing packages if any
if [ -n "$ESSENTIAL_PACKAGES" ]; then
    echo "  - Installing missing packages: $ESSENTIAL_PACKAGES"
    sudo apt update
    sudo apt install -y $ESSENTIAL_PACKAGES
    echo "  - Essential dependencies installed successfully"
else
    echo "  - All essential dependencies already installed"
fi

# Install Docker (handle WSL vs native)
echo "[2/9] Installing Docker..."
if [ "$IS_WSL" = true ]; then
    # Check if Docker Desktop is available (recommended for WSL)
    if command -v docker.exe &> /dev/null || command -v docker &> /dev/null; then
        echo "  - Docker already available in WSL environment"
        if command -v docker &> /dev/null; then
            echo "  - Docker version: $(docker --version)"
        else
            echo "  - Docker Desktop (Windows) detected"
            echo "  - Make sure Docker Desktop has WSL integration enabled"
        fi
    else
        echo "  - Installing Docker Engine for WSL..."
        sudo apt update
        
        # Install prerequisites
        sudo apt install -y \
            ca-certificates \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Set up the repository
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Start Docker service in WSL
        sudo service docker start
        
        echo "  - Docker Engine installed successfully for WSL"
    fi
else
    # Native Ubuntu installation
    echo "  - Installing Docker from Ubuntu repositories..."
    sudo apt update
    sudo apt install -y docker.io docker-compose-plugin
fi

# Add user to docker group
echo "[3/9] Adding $USER to docker group..."
if ! groups $USER | grep -q docker; then
    sudo usermod -aG docker $USER
    echo "  - Added $USER to docker group"
else
    echo "  - $USER already in docker group"
fi

# Install media dependencies
echo "[4/9] Installing media libraries..."
if [ "$IS_WSL" = true ]; then
    echo "  - Installing media libraries for WSL..."
    # In WSL, some GPU drivers might not be needed, but we'll install what we can
    sudo apt install -y \
        mpv \
        feh \
        libmpv2 2>/dev/null || echo "  - Note: Some packages may not be available in WSL"
else
    sudo apt install -y \
        mpv \
        feh \
        libmpv2 \
        libdrm-amdgpu1 \
        mesa-vulkan-drivers \
        vainfo
fi

# Install ROCm (if AMD GPU detected and not in WSL)
if [ "$IS_WSL" = true ]; then
    echo "[5/9] WSL detected - skipping ROCm installation"
    echo "  - For GPU support in WSL, ensure Docker Desktop has GPU access enabled"
elif command -v lspci &> /dev/null && lspci | grep -i amd | grep -qi vga; then
    echo "[5/9] AMD GPU detected, installing ROCm 6.2+..."
    
    # Add ROCm repository
    wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
    echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.2/ ubuntu main' | \
        sudo tee /etc/apt/sources.list.d/rocm.list
    
    sudo apt update
    sudo apt install -y rocm-hip-sdk rocminfo
    
    # Add user to render and video groups
    sudo usermod -aG render,video $USER
else
    echo "[5/9] No AMD GPU detected, skipping ROCm installation"
fi

# Apply system tuning (skip in WSL)
echo "[6/9] Applying kernel tuning..."
if [ "$IS_WSL" = true ]; then
    echo "  - WSL detected - skipping kernel tuning (managed by Windows)"
elif [ -f config/sysctl-hypno-hub.conf ]; then
    sudo cp config/sysctl-hypno-hub.conf /etc/sysctl.d/99-hypno-hub.conf
    sudo sysctl --system
else
    echo "  - Note: config/sysctl-hypno-hub.conf not found, skipping"
fi

# Create project directories
echo "[7/9] Creating project directories..."
mkdir -p hub/{media/{video,img,audio},scripts,logs}
touch hub/media/{video,img,audio}/.gitkeep
touch hub/{scripts,logs}/.gitkeep

# Set up environment file
echo "[8/9] Creating environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please review and customize"
else
    echo ".env already exists, skipping"
fi

# Build Docker image
echo "[9/9] Building Docker image..."
if [ "$IS_WSL" = true ]; then
    # In WSL, we might need to start Docker service first
    if ! docker info &> /dev/null; then
        echo "  - Starting Docker service..."
        sudo service docker start 2>/dev/null || echo "  - Docker service management may require Docker Desktop"
        sleep 2
    fi
fi

docker compose build

echo ""
echo "=== Setup Complete! ==="
echo ""
if [ "$IS_WSL" = true ]; then
    echo "WSL-specific notes:"
    echo "  - Docker Desktop WSL integration is recommended for best experience"
    echo "  - If using Docker Engine in WSL, you may need to start Docker manually: sudo service docker start"
    echo "  - For GUI features, consider setting up an X server on Windows (e.g., VcXsrv, X410)"
    echo ""
fi
echo "Next steps:"
if [ "$IS_WSL" = false ]; then
    echo "1. Log out and log back in for group membership to take effect"
else
    echo "1. Restart your WSL session (or run 'newgrp docker' to use docker without restart)"
fi
echo "2. Add your media files to hub/media/"
echo "3. (Optional) Install and configure Ollama on host"
echo "4. Start the service: docker compose up -d"
echo "5. Access the interface: http://localhost:9999"
echo ""
if [ "$IS_WSL" = false ]; then
    echo "For i3 WM kill-switch, add config/i3-config-snippet.conf to ~/.config/i3/config"
    echo ""
fi
