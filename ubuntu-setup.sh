#!/bin/bash
#
# Ubuntu 25.04 Setup Script for Hypno-Hub
# Run with: bash ubuntu-setup.sh
#

set -e

echo "=== Hypno-Hub Ubuntu 25.04 Setup ==="
echo ""

# Check Ubuntu version
if ! grep -q "25.04" /etc/os-release; then
    echo "Warning: This script is optimized for Ubuntu 25.04"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
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
    echo "  - pip3 already installed: $(pip3 --version | head -n1)"
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

# Install Docker (Ubuntu 25.04 native)
echo "[2/9] Installing Docker from Ubuntu repositories..."
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# Add user to docker group
echo "[3/9] Adding $USER to docker group..."
sudo usermod -aG docker $USER

# Install media dependencies
echo "[4/9] Installing media libraries..."
sudo apt install -y \
    mpv \
    feh \
    libmpv2 \
    libdrm-amdgpu1 \
    mesa-vulkan-drivers \
    vainfo

# Install ROCm (if AMD GPU detected)
if lspci | grep -i amd | grep -qi vga; then
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

# Apply system tuning
echo "[6/9] Applying kernel tuning..."
if [ -f config/sysctl-hypno-hub.conf ]; then
    sudo cp config/sysctl-hypno-hub.conf /etc/sysctl.d/99-hypno-hub.conf
    sudo sysctl --system
else
    echo "Warning: config/sysctl-hypno-hub.conf not found"
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
docker compose build

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Log out and log back in for group membership to take effect"
echo "2. Add your media files to hub/media/"
echo "3. (Optional) Install and configure Ollama on host"
echo "4. Start the service: docker compose up -d"
echo "5. Access the interface: http://localhost:9999"
echo ""
echo "For i3 WM kill-switch, add config/i3-config-snippet.conf to ~/.config/i3/config"
echo ""
