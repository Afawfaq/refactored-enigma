# Hypno-Hub Windows Setup Script with WSL Ubuntu Auto-Setup
# Run with: powershell -ExecutionPolicy Bypass -File windows-setup.ps1
#
# This script automatically:
# - Installs WSL with Ubuntu (if not present)
# - Installs Docker Desktop
# - Runs ubuntu-setup.sh inside WSL to complete setup

Write-Host "=== Hypno-Hub Windows Setup with WSL Ubuntu ===" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Administrator privileges are REQUIRED for WSL and dependency installation" -ForegroundColor Yellow
    Write-Host "Please run this script as Administrator by right-clicking PowerShell and selecting 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue without admin privileges? (Not recommended) (y/N)"
    if ($continue -notmatch '^[Yy]$') {
        Write-Host "Exiting. Please restart PowerShell as Administrator and run this script again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Continuing without admin - WSL installation will be skipped" -ForegroundColor Yellow
}

# Check and install WSL with Ubuntu
Write-Host "[1/10] Checking for WSL (Windows Subsystem for Linux)..." -ForegroundColor Green
$wslInstalled = $false
$wslNeedsReboot = $false

try {
    $wslVersion = wsl --version 2>&1
    $wslInstalled = $true
    Write-Host "WSL is installed" -ForegroundColor Gray
    
    # Check for Ubuntu distribution
    $wslDistros = wsl --list --quiet 2>&1 | Out-String
    if ($wslDistros -match "Ubuntu") {
        Write-Host "Ubuntu distribution found in WSL" -ForegroundColor Gray
    } else {
        Write-Host "No Ubuntu distribution found" -ForegroundColor Yellow
        if ($isAdmin) {
            Write-Host "Installing Ubuntu distribution..." -ForegroundColor Cyan
            wsl --install -d Ubuntu
            Write-Host "Ubuntu installed. You may need to restart and set up your Ubuntu user." -ForegroundColor Green
            $wslNeedsReboot = $true
        } else {
            Write-Host "Run as Administrator to install Ubuntu distribution" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "WSL not found or not enabled" -ForegroundColor Yellow
    
    if ($isAdmin) {
        Write-Host "Installing WSL with Ubuntu..." -ForegroundColor Cyan
        try {
            # Install WSL with Ubuntu as default distribution
            wsl --install -d Ubuntu
            Write-Host "WSL and Ubuntu installed successfully!" -ForegroundColor Green
            Write-Host "A system restart is required to complete WSL installation." -ForegroundColor Yellow
            $wslNeedsReboot = $true
        } catch {
            Write-Host "Failed to install WSL automatically" -ForegroundColor Red
            Write-Host "Please install WSL manually:" -ForegroundColor Cyan
            Write-Host "1. Open PowerShell as Administrator" -ForegroundColor White
            Write-Host "2. Run: wsl --install" -ForegroundColor White
            Write-Host "3. Restart your computer" -ForegroundColor White
            Write-Host "4. Run this script again" -ForegroundColor White
        }
    } else {
        Write-Host "Administrator privileges required to install WSL" -ForegroundColor Red
        Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
    }
}

# Check for winget (Windows Package Manager)
Write-Host "[2/10] Checking for Windows Package Manager (winget)..." -ForegroundColor Green
$wingetAvailable = $false
try {
    $wingetVersion = winget --version 2>&1
    Write-Host "winget found: $wingetVersion" -ForegroundColor Gray
    $wingetAvailable = $true
} catch {
    Write-Host "winget not found!" -ForegroundColor Yellow
    Write-Host "Windows Package Manager is recommended for automatic installation." -ForegroundColor Yellow
    Write-Host "You can install it from the Microsoft Store: 'App Installer'" -ForegroundColor Yellow
    Write-Host "Continuing with manual installation prompts..." -ForegroundColor Yellow
}

# Check and install Python 3
Write-Host "[3/10] Checking for Python 3..." -ForegroundColor Green
$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Gray
        $pythonInstalled = $true
    } else {
        throw "Python 3 not found"
    }
} catch {
    Write-Host "Python 3 not found!" -ForegroundColor Yellow
    
    if ($wingetAvailable -and $isAdmin) {
        Write-Host "Attempting to install Python 3 using winget..." -ForegroundColor Cyan
        try {
            # Install latest Python 3.x (3.12 is stable and widely used as of 2024)
            # Using 3.12 specifically ensures compatibility with the project requirements
            winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
            Write-Host "Python 3 installed successfully!" -ForegroundColor Green
            Write-Host "Note: You may need to restart PowerShell for PATH changes to take effect" -ForegroundColor Yellow
            $pythonInstalled = $true
        } catch {
            Write-Host "Failed to install Python automatically" -ForegroundColor Red
        }
    }
    
    if (-not $pythonInstalled) {
        Write-Host "To install Python 3 manually:" -ForegroundColor Cyan
        Write-Host "1. Download from: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Run the installer and CHECK 'Add Python to PATH'" -ForegroundColor White
        Write-Host "3. After installation, restart PowerShell and run this script again" -ForegroundColor White
        Write-Host "" -ForegroundColor Yellow
        $continue = Read-Host "Continue without Python? (y/N)"
        if ($continue -notmatch '^[Yy]$') {
            Write-Host "Exiting. Please install Python and run this script again." -ForegroundColor Yellow
            exit 1
        }
        Write-Host "Continuing without Python - some features may not work" -ForegroundColor Yellow
    }
}

# Check for pip (comes with Python)
Write-Host "[4/10] Checking for pip..." -ForegroundColor Green
try {
    $pipVersion = pip --version 2>&1
    Write-Host "pip found: $pipVersion" -ForegroundColor Gray
} catch {
    Write-Host "pip not found" -ForegroundColor Yellow
    # pip comes with modern Python installations by default
    # If Python was just installed, user may need to restart PowerShell for PATH updates
    Write-Host "pip should come with Python installation. If Python was just installed, restart PowerShell." -ForegroundColor Yellow
    Write-Host "Otherwise, you may need to reinstall Python with pip enabled" -ForegroundColor Yellow
}

# Check and install git
Write-Host "[5/10] Checking for git..." -ForegroundColor Green
$gitInstalled = $false
try {
    $gitVersion = git --version 2>&1
    Write-Host "git found: $gitVersion" -ForegroundColor Gray
    $gitInstalled = $true
} catch {
    Write-Host "git not found!" -ForegroundColor Yellow
    
    if ($wingetAvailable -and $isAdmin) {
        Write-Host "Attempting to install git using winget..." -ForegroundColor Cyan
        try {
            winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
            Write-Host "git installed successfully!" -ForegroundColor Green
            Write-Host "Note: You may need to restart PowerShell for PATH changes to take effect" -ForegroundColor Yellow
            $gitInstalled = $true
        } catch {
            Write-Host "Failed to install git automatically" -ForegroundColor Red
        }
    }
    
    if (-not $gitInstalled) {
        Write-Host "To install git manually:" -ForegroundColor Cyan
        Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor White
        Write-Host "Continuing without git..." -ForegroundColor Yellow
    }
}

# Check for Docker Desktop
Write-Host "[6/10] Checking for Docker Desktop..." -ForegroundColor Green
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
Write-Host "[7/10] Checking for Docker Compose..." -ForegroundColor Green
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
Write-Host "[8/10] Creating project directories..." -ForegroundColor Green
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
Write-Host "[9/10] Creating environment configuration..." -ForegroundColor Green
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

# Run Ubuntu setup inside WSL (if available and no reboot needed)
Write-Host "[10/10] Finalizing setup..." -ForegroundColor Green

if ($wslNeedsReboot) {
    Write-Host ""
    Write-Host "=== Restart Required ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WSL has been installed but requires a system restart." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restarting:" -ForegroundColor Cyan
    Write-Host "1. Open Ubuntu from the Start menu to complete initial setup" -ForegroundColor White
    Write-Host "2. Run: cd /mnt/c/Users/$env:USERNAME/path/to/refactored-enigma" -ForegroundColor White
    Write-Host "3. Run: bash ubuntu-setup.sh" -ForegroundColor White
    Write-Host "4. This will auto-install all dependencies in WSL Ubuntu" -ForegroundColor White
    Write-Host ""
    $restart = Read-Host "Would you like to restart now? (y/N)"
    if ($restart -match '^[Yy]$') {
        Write-Host "Restarting system..." -ForegroundColor Cyan
        Restart-Computer -Force
    }
    exit 0
}

# Check if WSL Ubuntu is available and run ubuntu-setup.sh
if ($wslInstalled) {
    try {
        Write-Host "Checking WSL Ubuntu availability..." -ForegroundColor Cyan
        $wslDistros = wsl --list --quiet 2>&1 | Out-String
        
        if ($wslDistros -match "Ubuntu") {
            Write-Host "Running ubuntu-setup.sh in WSL to auto-install all dependencies..." -ForegroundColor Cyan
            Write-Host ""
            
            # Get current directory in Windows path format
            $currentDir = Get-Location
            # Convert Windows path to WSL path
            $wslPath = $currentDir.Path -replace '\\', '/' -replace 'C:', '/mnt/c'
            
            Write-Host "Executing setup in WSL Ubuntu..." -ForegroundColor Green
            Write-Host "(This will auto-install Docker, Python, git, and all dependencies)" -ForegroundColor Gray
            Write-Host ""
            
            # Run the ubuntu-setup.sh script in WSL
            wsl -d Ubuntu bash -c "cd '$wslPath' && bash ubuntu-setup.sh"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "=== WSL Ubuntu Setup Complete! ===" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "All dependencies have been auto-installed in WSL Ubuntu!" -ForegroundColor Green
                Write-Host ""
                Write-Host "Next steps:" -ForegroundColor Yellow
                Write-Host "1. To use from WSL Ubuntu:" -ForegroundColor Cyan
                Write-Host "   - Open Ubuntu from Start menu" -ForegroundColor White
                Write-Host "   - cd $wslPath" -ForegroundColor White
                Write-Host "   - docker compose up -d" -ForegroundColor White
                Write-Host ""
                Write-Host "2. To use from Windows:" -ForegroundColor Cyan
                Write-Host "   - Make sure Docker Desktop has WSL integration enabled" -ForegroundColor White
                Write-Host "   - docker compose -f docker-compose.windows.yml up -d" -ForegroundColor White
                Write-Host ""
                Write-Host "3. Access the interface at: http://localhost:9999" -ForegroundColor White
                Write-Host ""
            } else {
                Write-Host "WSL setup encountered issues. Falling back to Windows-only setup..." -ForegroundColor Yellow
                Write-Host "Building Docker image for Windows..." -ForegroundColor Green
                docker compose -f docker-compose.windows.yml build
            }
        } else {
            Write-Host "Ubuntu not found in WSL, building for Windows..." -ForegroundColor Yellow
            docker compose -f docker-compose.windows.yml build
        }
    } catch {
        Write-Host "Could not run WSL setup: $_" -ForegroundColor Yellow
        Write-Host "Building Docker image for Windows..." -ForegroundColor Green
        docker compose -f docker-compose.windows.yml build
    }
} else {
    # WSL not available, build for Windows
    Write-Host "Building Docker image for Windows..." -ForegroundColor Green
    docker compose -f docker-compose.windows.yml build
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Setup Complete! ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Recommended: Use WSL Ubuntu for the best experience" -ForegroundColor Yellow
    if (-not $wslInstalled) {
        Write-Host "  - WSL provides full Linux compatibility and better performance" -ForegroundColor Gray
        Write-Host "  - Run this script as Administrator to auto-install WSL" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Add your media files to hub\media\" -ForegroundColor White
    Write-Host "2. (Optional) Install Ollama on Windows from: https://ollama.ai/download" -ForegroundColor White
    Write-Host "3. Start the service: docker compose up -d" -ForegroundColor White
    Write-Host "4. Access the interface: http://localhost:9999" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Error: Setup encountered issues" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    exit 1
}
