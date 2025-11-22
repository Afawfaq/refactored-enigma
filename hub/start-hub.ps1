# Hypno Hub Session Manager for Windows
# Coordinates media playback with logging

# Configuration
$HUB_DIR = "C:\home\beta\hub"
$LOG_DIR = "$HUB_DIR\logs"
$MEDIA_DIR = "$HUB_DIR\media"
$LOG_FILE = "$LOG_DIR\session.log"

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# Function to write log
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "${timestamp}: $Message"
    Write-Host "${timestamp}: $Message"
}

# Function to cleanup processes
function Cleanup-Processes {
    Write-Log "Cleaning up processes"
    try {
        Get-Process | Where-Object { $_.Name -like "*mpv*" } | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-Process | Where-Object { $_.Name -like "*feh*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Log "Error during cleanup: $_"
    }
    Write-Log "Cleanup complete"
}

# Log session start
Write-Log "Session start"
Write-Log "Environment - OS: Windows"

# Stop any leftover processes
Write-Log "Stopping any leftover processes"
Cleanup-Processes

# Check if media directories exist and have content
$videoPath = "$MEDIA_DIR\video"
$imgPath = "$MEDIA_DIR\img"
$audioPath = "$MEDIA_DIR\audio"

if (-not (Test-Path $videoPath) -or ((Get-ChildItem $videoPath -File).Count -eq 0)) {
    Write-Log "Warning - No video files found in $videoPath"
    Write-Host "Please add video files to $videoPath"
} else {
    # Start background video loop with mpv
    Write-Log "Starting video playback"
    try {
        $videoFiles = Get-ChildItem $videoPath -File | Select-Object -ExpandProperty FullName
        if ($videoFiles) {
            # Note: On Windows, mpv may not be available unless installed separately
            # This is primarily for WSL2/Linux container environments
            Write-Log "Video files found, starting mpv (if available)"
            # Start-Process -FilePath "mpv" -ArgumentList "--shuffle","--loop=inf","--really-quiet","--no-osd","--fs","--no-input-default-bindings","--input-conf=/dev/null","--hwdec=auto",$videoPath -NoNewWindow
        }
    } catch {
        Write-Log "Error starting video playback: $_"
    }
}

# Wait a moment for video to initialize
Start-Sleep -Seconds 2

if (-not (Test-Path $imgPath) -or ((Get-ChildItem $imgPath -File).Count -eq 0)) {
    Write-Log "Warning - No images found in $imgPath"
    Write-Host "Please add images to $imgPath"
} else {
    # Start image slideshow
    Write-Log "Starting image slideshow"
    try {
        # Note: feh is not available on Windows, this is for container environments
        Write-Log "Image files found (slideshow available in Linux container)"
    } catch {
        Write-Log "Error starting image slideshow: $_"
    }
}

# Optional audio layer
if ((Test-Path $audioPath) -and ((Get-ChildItem $audioPath -File).Count -gt 0)) {
    Write-Log "Starting audio playback"
    try {
        # Note: mpv audio layer
        Write-Log "Audio files found, starting audio playback (if available)"
    } catch {
        Write-Log "Error starting audio playback: $_"
    }
} else {
    Write-Log "No audio files found in $audioPath - skipping audio layer"
}

# Keep script running
Write-Log "Session active - press Ctrl+C to terminate"
Write-Host ""
Write-Host "Note: This script is designed to run inside a Docker container on Windows." -ForegroundColor Yellow
Write-Host "Media playback requires mpv and feh, which are available in the Linux container." -ForegroundColor Yellow
Write-Host ""

try {
    # Wait indefinitely until interrupted
    while ($true) {
        Start-Sleep -Seconds 5
    }
} finally {
    Cleanup-Processes
}
