#!/bin/bash
#
# Hypno Hub Session Manager
# Coordinates video, image, and audio playback with logging
#

set -e

export DISPLAY=${DISPLAY:-:0}
export PATH="$PATH:/usr/bin:/usr/local/bin"

# Configuration
HUB_DIR="/home/beta/hub"
LOG_DIR="$HUB_DIR/logs"
MEDIA_DIR="$HUB_DIR/media"
LOG_FILE="$LOG_DIR/session.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log session start
echo "$(date): Session start" >> "$LOG_FILE"
echo "$(date): Environment - DISPLAY=$DISPLAY" >> "$LOG_FILE"

# Function to cleanup processes
cleanup() {
    echo "$(date): Cleaning up processes" >> "$LOG_FILE"
    pkill -f mpv 2>/dev/null || true
    pkill -f feh 2>/dev/null || true
    echo "$(date): Cleanup complete" >> "$LOG_FILE"
}

# Trap exit signals
trap cleanup EXIT INT TERM

# Stop any leftover processes
echo "$(date): Stopping any leftover processes" >> "$LOG_FILE"
cleanup

# Check if media directories exist and have content
if [ ! -d "$MEDIA_DIR/video" ] || [ -z "$(ls -A $MEDIA_DIR/video 2>/dev/null)" ]; then
    echo "$(date): Warning - No video files found in $MEDIA_DIR/video" >> "$LOG_FILE"
    echo "Please add video files to $MEDIA_DIR/video"
else
    # Start background video loop
    echo "$(date): Starting video playback" >> "$LOG_FILE"
    mpv --shuffle --loop=inf --really-quiet --no-osd \
        --fs --no-input-default-bindings --input-conf=/dev/null \
        --hwdec=auto \
        "$MEDIA_DIR/video" >> "$LOG_FILE" 2>&1 &
    VIDEO_PID=$!
    echo "$(date): Video player started (PID: $VIDEO_PID)" >> "$LOG_FILE"
fi

# Wait a moment for video to initialize
sleep 2

if [ ! -d "$MEDIA_DIR/img" ] || [ -z "$(ls -A $MEDIA_DIR/img 2>/dev/null)" ]; then
    echo "$(date): Warning - No images found in $MEDIA_DIR/img" >> "$LOG_FILE"
    echo "Please add images to $MEDIA_DIR/img"
else
    # Start image slideshow overlay
    echo "$(date): Starting image slideshow" >> "$LOG_FILE"
    feh --fullscreen --randomize --slideshow-delay 10 \
        --hide-pointer --quiet \
        "$MEDIA_DIR/img" >> "$LOG_FILE" 2>&1 &
    FEH_PID=$!
    echo "$(date): Image slideshow started (PID: $FEH_PID)" >> "$LOG_FILE"
fi

# Optional binaural audio layer
if [ -d "$MEDIA_DIR/audio" ] && [ -n "$(ls -A $MEDIA_DIR/audio 2>/dev/null)" ]; then
    echo "$(date): Starting audio playback" >> "$LOG_FILE"
    mpv --shuffle --loop=inf --really-quiet --no-video \
        --volume=70 \
        "$MEDIA_DIR/audio" >> "$LOG_FILE" 2>&1 &
    AUDIO_PID=$!
    echo "$(date): Audio player started (PID: $AUDIO_PID)" >> "$LOG_FILE"
else
    echo "$(date): No audio files found in $MEDIA_DIR/audio - skipping audio layer" >> "$LOG_FILE"
fi

# Keep script running and wait for processes
echo "$(date): Session active - waiting for termination signal" >> "$LOG_FILE"
wait
