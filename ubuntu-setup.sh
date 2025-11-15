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

# Install Docker (Ubuntu 25.04 native)
echo "[1/8] Installing Docker from Ubuntu repositories..."
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# Add user to docker group
echo "[2/8] Adding $USER to docker group..."
sudo usermod -aG docker $USER

# Install media dependencies
echo "[3/8] Installing media libraries..."
sudo apt install -y \
    mpv \
    feh \
    libmpv2 \
    libdrm-amdgpu1 \
    mesa-vulkan-drivers \
    vainfo

# Install ROCm (if AMD GPU detected)
if lspci | grep -i amd | grep -qi vga; then
    echo "[4/8] AMD GPU detected, installing ROCm 6.2+..."
    
    # Add ROCm repository
    wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
    echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.2/ ubuntu main' | \
        sudo tee /etc/apt/sources.list.d/rocm.list
    
    sudo apt update
    sudo apt install -y rocm-hip-sdk rocminfo
    
    # Add user to render and video groups
    sudo usermod -aG render,video $USER
else
    echo "[4/8] No AMD GPU detected, skipping ROCm installation"
fi

# Apply system tuning
echo "[5/8] Applying kernel tuning..."
if [ -f config/sysctl-hypno-hub.conf ]; then
    sudo cp config/sysctl-hypno-hub.conf /etc/sysctl.d/99-hypno-hub.conf
    sudo sysctl --system
else
    echo "Warning: config/sysctl-hypno-hub.conf not found"
fi

# Create project directories
echo "[6/8] Creating project directories..."
mkdir -p hub/{media/{video,img,audio},scripts,logs}
touch hub/media/{video,img,audio}/.gitkeep
touch hub/{scripts,logs}/.gitkeep

# Set up environment file
echo "[7/8] Creating environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please review and customize"
else
    echo ".env already exists, skipping"
fi

# Build Docker image
echo "[8/8] Building Docker image..."
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
