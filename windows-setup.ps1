# Hypno-Hub Windows Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File windows-setup.ps1

Write-Host "=== Hypno-Hub Windows Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some steps may require administrator privileges" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -notmatch '^[Yy]$') {
        exit 1
    }
}

# Check for Docker Desktop
Write-Host "[1/6] Checking for Docker Desktop..." -ForegroundColor Green
try {
    $dockerVersion = docker --version
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Gray
} catch {
    Write-Host "Docker Desktop not found!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "After installation, restart this script." -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
Write-Host "[2/6] Checking for Docker Compose..." -ForegroundColor Green
try {
    $composeVersion = docker compose version
    Write-Host "Docker Compose found: $composeVersion" -ForegroundColor Gray
} catch {
    Write-Host "Docker Compose not found!" -ForegroundColor Red
    Write-Host "Docker Compose should come with Docker Desktop." -ForegroundColor Yellow
    Write-Host "Please reinstall Docker Desktop or update it." -ForegroundColor Yellow
    exit 1
}

# Create project directories
Write-Host "[3/6] Creating project directories..." -ForegroundColor Green
$directories = @(
    "hub\media\video",
    "hub\media\img",
    "hub\media\audio",
    "hub\scripts",
    "hub\logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        # Create .gitkeep file
        New-Item -ItemType File -Path "$dir\.gitkeep" -Force | Out-Null
    }
}
Write-Host "Directories created successfully" -ForegroundColor Gray

# Set up environment file
Write-Host "[4/6] Creating environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file - please review and customize" -ForegroundColor Gray
} else {
    Write-Host ".env already exists, skipping" -ForegroundColor Gray
}

# Update .env for Windows
Write-Host "[5/6] Updating .env for Windows..." -ForegroundColor Green
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    # Use host.docker.internal for Ollama on Windows
    if ($envContent -match "OLLAMA_HOST=") {
        $envContent = $envContent -replace "OLLAMA_HOST=.*", "OLLAMA_HOST=http://host.docker.internal:11434"
    }
    Set-Content ".env" $envContent
    Write-Host "Environment file updated for Windows" -ForegroundColor Gray
}

# Build Docker image
Write-Host "[6/6] Building Docker image..." -ForegroundColor Green
docker compose -f docker-compose.windows.yml build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Setup Complete! ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Add your media files to hub\media\" -ForegroundColor White
    Write-Host "2. (Optional) Install Ollama on Windows from: https://ollama.ai/download" -ForegroundColor White
    Write-Host "3. Start the service: docker compose up -d" -ForegroundColor White
    Write-Host "4. Access the interface: http://localhost:9999" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: On Windows, media playback happens inside the Docker container." -ForegroundColor Yellow
    Write-Host "For the best experience, use WSL2 or a dedicated Linux VM." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    exit 1
}
