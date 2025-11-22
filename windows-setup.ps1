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

# Check for Python 3
Write-Host "[1/8] Checking for Python 3..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Gray
    } else {
        throw "Python 3 not found"
    }
} catch {
    Write-Host "Python 3 not found!" -ForegroundColor Yellow
    Write-Host "Python is required to run validation scripts and utilities." -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "To install Python 3:" -ForegroundColor Cyan
    Write-Host "1. Download from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. Run the installer and CHECK 'Add Python to PATH'" -ForegroundColor White
    Write-Host "3. After installation, restart PowerShell and run this script again" -ForegroundColor White
    Write-Host "" -ForegroundColor Yellow
    $installPython = Read-Host "Continue without Python? (y/N)"
    if ($installPython -notmatch '^[Yy]$') {
        Write-Host "Exiting. Please install Python and run this script again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Continuing without Python - some features may not work" -ForegroundColor Yellow
}

# Check for pip
Write-Host "[2/8] Checking for pip..." -ForegroundColor Green
try {
    $pipVersion = pip --version 2>&1
    Write-Host "pip found: $pipVersion" -ForegroundColor Gray
} catch {
    Write-Host "pip not found - it should come with Python installation" -ForegroundColor Yellow
    Write-Host "You may need to reinstall Python with pip enabled" -ForegroundColor Yellow
}

# Check for git
Write-Host "[3/8] Checking for git..." -ForegroundColor Green
try {
    $gitVersion = git --version 2>&1
    Write-Host "git found: $gitVersion" -ForegroundColor Gray
} catch {
    Write-Host "git not found!" -ForegroundColor Yellow
    Write-Host "Git is useful for version control and updates." -ForegroundColor Yellow
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "Continuing without git..." -ForegroundColor Yellow
}

# Check for Docker Desktop
Write-Host "[4/8] Checking for Docker Desktop..." -ForegroundColor Green
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
Write-Host "[5/8] Checking for Docker Compose..." -ForegroundColor Green
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
Write-Host "[6/8] Creating project directories..." -ForegroundColor Green
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
Write-Host "[7/8] Creating environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file - please review and customize" -ForegroundColor Gray
} else {
    Write-Host ".env already exists, skipping" -ForegroundColor Gray
}

# Update .env for Windows
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    # Use host.docker.internal for Ollama on Windows
    # Match only actual OLLAMA_HOST variable assignments
    if ($envContent -match "^\s*OLLAMA_HOST\s*=") {
        $envContent = $envContent -replace "^\s*OLLAMA_HOST\s*=.*$", "OLLAMA_HOST=http://host.docker.internal:11434" -replace "(?m)"
    }
    Set-Content ".env" $envContent
    Write-Host "Environment file updated for Windows" -ForegroundColor Gray
}

# Build Docker image
Write-Host "[8/8] Building Docker image..." -ForegroundColor Green
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
