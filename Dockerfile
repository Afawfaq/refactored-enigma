FROM python:3.13-slim

# Ubuntu 25.04 optimized - Python 3.13 matches host kernel 6.14
LABEL maintainer="Hypno-Hub"
LABEL description="Ubuntu 25.04 Plucky Puffin optimized immersive media system"

# Install system dependencies optimized for Ubuntu 25.04
RUN apt-get update && apt-get install -y \
    libmpv2 \
    mpv \
    feh \
    curl \
    procps \
    libdrm-amdgpu1 \
    mesa-vulkan-drivers \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/beta/hub

# Copy application files
COPY hub /home/beta/hub

# Install Python dependencies (torch 2.9+ has Ubuntu 25.04 wheels)
RUN pip3 install --no-cache-dir --user \
    flask \
    requests \
    torch \
    torchvision \
    torchaudio

# Make start script executable
RUN chmod +x /home/beta/hub/start-hub.sh

# Expose the web interface port
EXPOSE 9999

# Create non-root user for security
RUN useradd -m -u 1000 hypnouser && \
    chown -R hypnouser:hypnouser /home/beta/hub

# Switch to non-root user
USER hypnouser

# Run the launcher
CMD ["python3", "launcher.py"]
