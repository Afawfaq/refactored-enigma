# Hypno-Hub: Ubuntu 25.04 "Plucky Puffin" Edition

## Overview

A privacy-first, containerized system for consensual immersive media experiences. Built specifically for Ubuntu 25.04's modern kernel and toolchain stack, leveraging kernel 6.14's enhanced AMDGPU support and Docker's latest security features.

### Core Philosophy
- **Explicit Consent**: Sessions cannot begin without active, informed user acknowledgment
- **Instant Escape**: Physical kill-switch (`Alt+Shift+E`) terminates all media immediately  
- **Complete Isolation**: Air-gapped Docker container with no network access
- **Local-Only AI**: Ollama runs on host; GPU passthrough ensures zero data exfiltration

---

## Ubuntu 25.04-Specific Features

### Why Ubuntu 25.04?

- **Kernel 6.14**: Enhanced AMDGPU driver with better 7800 XT support
- **Python 3.13**: Latest Python with performance improvements
- **Docker 28+**: Native package with improved security sandboxing
- **ROCm 6.2+**: Full RDNA 3 support for AI workloads
- **Mesa 24.x**: Improved Vulkan and VA-API hardware acceleration

---

## Prerequisites

### Host System
- **Proxmox VE 8.3+** with AMD 7800 XT GPU passthrough configured
- **Guest VM**: Ubuntu 25.04 Desktop with minimum 4GB RAM, 10GB disk
- **GPU Passthrough**: Configured via Proxmox (see Proxmox GPU Passthrough section)

### Software Requirements
- **Kernel 6.14+**: `uname -r` should show 6.14.x
- **Docker 28+**: Native Ubuntu 25.04 package
- **ROCm 6.2+**: For AI features (optional)
- **X11 or XWayland**: For display forwarding

---

## Quick Start (Ubuntu 25.04)

### Automated Setup

```bash
# Clone the repository
git clone https://github.com/Afawfaq/refactored-enigma.git
cd refactored-enigma

# Run the setup script
bash ubuntu-setup.sh

# Log out and back in for group membership
# Then start the service
docker compose up -d

# Access at http://localhost:9999
```

### Manual Setup

#### 1. Install Docker (Ubuntu 25.04 Native)

Ubuntu 25.04 includes Docker 28.x directly in the `universe` repository:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

**Note**: No need for Docker's official repository on 25.04; the packaged version is current.

#### 2. Install Media Dependencies

```bash
sudo apt install -y \
    mpv \
    feh \
    libmpv2 \
    libdrm-amdgpu1 \
    mesa-vulkan-drivers \
    vainfo
```

#### 3. Install ROCm 6.2+ (for AMD GPU)

```bash
# Add ROCm repository
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.2/ ubuntu main' | \
    sudo tee /etc/apt/sources.list.d/rocm.list

# Install ROCm
sudo apt update
sudo apt install -y rocm-hip-sdk rocminfo

# Add user to required groups
sudo usermod -aG render,video $USER
```

#### 4. Create Project Structure

```bash
mkdir -p hub/{media/{video,img,audio},scripts,logs}
touch hub/media/{video,img,audio}/.gitkeep
```

#### 5. Build and Run

```bash
# Copy environment template
cp .env.example .env

# Build Docker image
docker compose build

# Start the service
docker compose up -d

# Check logs
docker compose logs -f hypno-hub
```

---

## Ollama Integration (Ubuntu 25.04)

### Simple TCP Setup (Recommended)

Install Ollama on the Ubuntu 25.04 guest or Proxmox host - it will be accessible via TCP:

**On Ubuntu 25.04 Guest (Simplest):**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl enable --now ollama

# Pull a model
ollama pull llama3.1:8b  # 4.7GB, fits in 7800 XT's 16GB VRAM
```

The Docker container will automatically connect via `http://host.docker.internal:11434` (TCP).

**On Proxmox Host (For resource sharing):**

```bash
# Install Ollama on Proxmox host
curl -fsSL https://ollama.com/install.sh | sh

# Configure Ollama to listen on all interfaces
sudo systemctl edit ollama
```

Add to the override file:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Reload and start:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Pull model
ollama pull llama3.1:8b

# Allow access from guest VM (replace 192.168.1.0/24 with your network)
sudo ufw allow from 192.168.1.0/24 to any port 11434
```

Then on Ubuntu 25.04 guest, update `.env`:
```bash
# Use actual Proxmox host IP
OLLAMA_HOST=http://192.168.1.100:11434
```

### Verify Connection

```bash
# Test from host/guest
curl http://localhost:11434/api/tags

# Test from Docker container
docker compose exec hypno-hub curl http://host.docker.internal:11434/api/tags

# Test AI script generation
docker compose exec hypno-hub python3 /home/beta/hub/ai_llm.py
```

---

## GPU Passthrough (Proxmox to Ubuntu 25.04)

### Proxmox Host Configuration

#### 1. Enable IOMMU

Edit `/etc/default/grub`:
```bash
# For AMD CPU:
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt video=efifb:off"

# For Intel CPU:
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt video=efifb:off"
```

Update GRUB:
```bash
sudo update-grub
sudo reboot
```

#### 2. Load VFIO Modules

Edit `/etc/modules`:
```
vfio
vfio_iommu_type1
vfio_pci
vfio_virqfd
```

Create `/etc/modprobe.d/vfio.conf`:
```bash
# Find your GPU PCI IDs
lspci -nn | grep -i amd | grep -i vga
# Example output: 01:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Navi 32 [Radeon RX 7800 XT] [1002:747e]

# Add IDs to vfio (replace with your IDs)
options vfio-pci ids=1002:747e,1002:ab30
```

Update initramfs:
```bash
sudo update-initramfs -u
sudo reboot
```

#### 3. Configure VM

In Proxmox web UI:
- **Hardware** → **Add** → **PCI Device**
- Select AMD GPU (01:00.0)
- Enable: **All Functions**, **Primary GPU**, **PCI-Express**, **ROM-Bar**

Set machine type to `q35` and add:
```bash
# In VM config (/etc/pve/qemu-server/<vmid>.conf)
args: -cpu host,kvm=off,hv_vendor_id=proxmox
```

### Ubuntu 25.04 Guest Verification

```bash
# Check GPU is detected
lspci | grep -i amd

# Verify kernel driver
lspci -k | grep -A 3 VGA

# Test ROCm
/opt/rocm/bin/rocminfo

# Check AMDGPU
dmesg | grep amdgpu

# Test hardware acceleration
vainfo
```

---

## System Tuning (Ubuntu 25.04)

### Kernel Parameters

Copy the provided sysctl configuration:
```bash
sudo cp config/sysctl-hypno-hub.conf /etc/sysctl.d/99-hypno-hub.conf
sudo sysctl --system
```

Or manually add to `/etc/sysctl.d/99-hypno-hub.conf`:
```ini
vm.swappiness=10
fs.inotify.max_user_watches=524288
fs.file-max=2097152
kernel.sched_latency_ns=6000000
```

### Kill-Switch Configuration (i3 WM)

If using i3 window manager, add to `~/.config/i3/config`:
```bash
# Copy snippet
cat config/i3-config-snippet.conf >> ~/.config/i3/config

# Reload i3
i3-msg reload
```

For GNOME, create a custom keyboard shortcut:
```bash
# Settings → Keyboard → Custom Shortcuts
# Name: Hypno-Hub Kill-Switch
# Command: pkill -f mpv; pkill -f feh
# Shortcut: Alt+Shift+E
```

---

## Security Configuration

### AppArmor (Ubuntu 25.04)

Ubuntu 25.04 has stricter AppArmor defaults. Allow Docker GPU access:

```bash
# Check AppArmor status
sudo aa-status

# Disable Docker profile (if causing issues)
sudo ln -s /etc/apparmor.d/docker /etc/apparmor.d/disable/
sudo apparmor_parser -R /etc/apparmor.d/docker
sudo systemctl restart docker
```

### Audit Logging

Enable systemd audit for session tracking:

```bash
# Install auditd
sudo apt install -y auditd

# Add audit rule
sudo auditctl -w /home/$USER/refactored-enigma/hub/ -p warx -k hypno-access

# Make persistent
echo "-w /home/$USER/refactored-enigma/hub/ -p warx -k hypno-access" | \
    sudo tee -a /etc/audit/rules.d/hypno-hub.rules

# Restart auditd
sudo systemctl restart auditd

# View logs
sudo ausearch -k hypno-access
```

### Air-Gapped Mode

For maximum privacy, disable network access in `docker-compose.yml`:

```yaml
services:
  hypno-hub:
    network_mode: "none"  # Completely isolated
```

**Note**: This disables Ollama network access. Use Unix socket method instead.

---

## Ubuntu 25.04-Specific Troubleshooting

### Issue 1: `mpv` Fails with "Cannot open display"

**Cause**: Wayland session doesn't properly expose X11 socket

**Solutions**:

```bash
# Option A: Use X11 session (recommended)
# Log out, select "Ubuntu on Xorg" at login screen

# Option B: Enable XWayland forwarding
export GDK_BACKEND=x11
docker compose restart

# Option C: Grant X11 access
xhost +local:docker
```

### Issue 2: ROCm "gfx1101 not found"

**Cause**: Ubuntu 25.04's kernel 6.14 requires ROCm 6.2+

**Solution**:

```bash
# Remove old ROCm
sudo apt purge rocm-*

# Install ROCm 6.2+
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.2/ ubuntu main' | \
    sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install -y rocm-hip-sdk

# Verify
/opt/rocm/bin/rocminfo | grep gfx1101
```

### Issue 3: Docker Build Context > 10GB

**Cause**: Ubuntu 25.04's GNOME 48 caches large thumbnails

**Solution**:

Ensure `.dockerignore` includes:
```
.cache/thumbnails/
.cache/gnome-software/
.cache/ibus/
```

Or clean cache:
```bash
rm -rf ~/.cache/thumbnails/*
rm -rf ~/.cache/gnome-software/*
```

### Issue 4: Permission Denied on `/dev/kfd`

**Cause**: User not in `render` group

**Solution**:

```bash
sudo usermod -aG render,video $USER
newgrp render

# Verify
groups | grep render
```

### Issue 5: Ollama Connection Timeout

**Cause**: Firewall blocking host communication

**Solution**:

```bash
# Allow Docker to host communication
sudo ufw allow from 172.17.0.0/16 to any port 11434

# Test from container
docker compose exec hypno-hub curl http://host.docker.internal:11434/api/tags
```

### Issue 6: Black Screen on Session Start

**Cause**: No media files or GPU acceleration failing

**Solutions**:

```bash
# Check media exists
ls -lh hub/media/video/
ls -lh hub/media/img/

# Test GPU acceleration
docker compose exec hypno-hub vainfo

# Check session logs
docker compose exec hypno-hub cat /home/beta/hub/logs/session.log

# Test mpv manually
docker compose exec hypno-hub mpv --version
```

---

## Performance Optimization

### For 7800 XT (RDNA 3)

Add to `.env`:
```bash
HSA_OVERRIDE_GFX_VERSION=11.0.0
ROCR_VISIBLE_DEVICES=0
HCC_AMDGPU_TARGET=gfx1101
ROC_ENABLE_PRE_VEGA=0
```

### For Low-End Systems

Reduce Docker resource limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

Use smaller Ollama model:
```bash
ollama pull llama3.1:3b  # 2GB instead of 4.7GB
```

---

## Development Mode

### Live Code Editing

```bash
# Volumes are already bind-mounted
# Edit files in hub/ and they'll reflect immediately

# Restart Flask without rebuilding
docker compose restart hypno-hub
```

### Debugging

```bash
# Access container shell
docker compose exec hypno-hub /bin/bash

# Check Python environment
docker compose exec hypno-hub python3 --version
docker compose exec hypno-hub pip list

# Test Ollama connection
docker compose exec hypno-hub python3 /home/beta/hub/ai_llm.py
```

---

## Building Custom ISO (Advanced)

Create a bootable Ubuntu 25.04 image with Hypno-Hub pre-installed:

```bash
# Install ubuntu-autoinstall
sudo apt install ubuntu-autoinstall cubic

# Download Ubuntu 25.04 ISO
wget https://releases.ubuntu.com/25.04/ubuntu-25.04-desktop-amd64.iso

# Use Cubic or manual cloud-init
# ... (Advanced users only)
```

---

## Updating

### Update Docker Images

```bash
# Pull latest base images
docker compose pull

# Rebuild
docker compose build --no-cache

# Restart
docker compose up -d
```

### Update Ollama Models

```bash
ollama pull llama3.1:8b
```

### Update System

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Uninstallation

```bash
# Stop and remove containers
docker compose down -v

# Remove Docker images
docker rmi $(docker images -q hypno-hub)

# Remove project (WARNING: deletes all media!)
cd .. && rm -rf refactored-enigma

# Optional: Remove Docker
sudo apt purge docker.io docker-compose-plugin
sudo apt autoremove
```

---

## FAQ

### Q: Why Ubuntu 25.04 specifically?

A: Kernel 6.14 has significantly improved AMDGPU support for RDNA 3 (7800 XT), and Python 3.13 offers better performance. Docker 28 also has enhanced security features.

### Q: Can I use this on Ubuntu 24.04 LTS?

A: Yes, but you'll need to manually install newer ROCm and may experience GPU issues. Recommended to use 25.04 or later.

### Q: Does this work without a GPU?

A: Yes, but AI features will be slower. Remove GPU-related lines from `docker-compose.yml`.

### Q: Is internet required?

A: Only for initial setup and pulling Ollama models. After that, it works fully offline in air-gapped mode.

### Q: How do I add custom scripts?

A: Place text files in `hub/scripts/` or use the AI generation feature via `ai_llm.py`.

---

## Support

For Ubuntu 25.04-specific issues:

```bash
# Check kernel version
uname -r

# Verify GPU
lspci | grep -i amd

# Check ROCm
/opt/rocm/bin/rocminfo

# Docker GPU test
docker run --rm --device=/dev/kfd --device=/dev/dri ubuntu:25.04 ls -l /dev/dri
```

### Getting Help

1. Check this guide's troubleshooting section
2. View container logs: `docker compose logs -f`
3. Open GitHub issue with:
   - Ubuntu version: `lsb_release -a`
   - Kernel: `uname -r`
   - Docker: `docker --version`
   - Error logs

---

## License

MIT License. Use responsibly and ethically.

**By using this software on Ubuntu 25.04, you agree to prioritize consent, safety, and autonomy above all else.**
