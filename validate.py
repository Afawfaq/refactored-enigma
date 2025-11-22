#!/usr/bin/env python3
"""
Validation script for Hypno-Hub installation.
Checks that all components are properly set up.
"""

import sys
import os
import subprocess
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_status(message, status="info"):
    """Print a colored status message."""
    if status == "success":
        print(f"{GREEN}✓{RESET} {message}")
    elif status == "error":
        print(f"{RED}✗{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"{BLUE}ℹ{RESET} {message}")


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print_status(f"{description} exists: {filepath}", "success")
        return True
    else:
        print_status(f"{description} missing: {filepath}", "error")
        return False


def check_directory_exists(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print_status(f"{description} exists: {dirpath}", "success")
        return True
    else:
        print_status(f"{description} missing: {dirpath}", "error")
        return False


def check_python_syntax(filepath):
    """Check Python file for syntax errors."""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        print_status(f"Python syntax valid: {filepath}", "success")
        return True
    except SyntaxError as e:
        print_status(f"Python syntax error in {filepath}: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Error checking {filepath}: {e}", "error")
        return False


def check_docker_file():
    """Check Dockerfile syntax."""
    if not check_file_exists("Dockerfile", "Dockerfile"):
        return False
    
    try:
        # Basic validation - check key instructions
        with open("Dockerfile", 'r') as f:
            content = f.read()
            
        required = ["FROM", "WORKDIR", "COPY", "CMD"]
        for keyword in required:
            if keyword not in content:
                print_status(f"Dockerfile missing {keyword} instruction", "warning")
        
        print_status("Dockerfile structure looks valid", "success")
        return True
    except Exception as e:
        print_status(f"Error checking Dockerfile: {e}", "error")
        return False


def check_docker_compose():
    """Check docker-compose.yml."""
    if not check_file_exists("docker-compose.yml", "Docker Compose file"):
        return False
    
    try:
        result = subprocess.run(
            ["docker", "compose", "config"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            print_status("Docker Compose configuration is valid", "success")
            return True
        else:
            print_status(f"Docker Compose validation failed: {result.stderr}", "error")
            return False
    except FileNotFoundError:
        print_status("Docker not found - skipping Docker Compose validation", "warning")
        return False
    except subprocess.TimeoutExpired:
        print_status("Docker Compose validation timed out", "warning")
        return False
    except Exception as e:
        print_status(f"Error checking Docker Compose: {e}", "error")
        return False


def check_media_directories():
    """Check media directory structure."""
    base_dir = Path("hub/media")
    required_dirs = ["video", "img", "audio"]
    
    all_exist = True
    for subdir in required_dirs:
        path = base_dir / subdir
        if not check_directory_exists(str(path), f"Media directory {subdir}"):
            all_exist = False
    
    return all_exist


def main():
    """Run all validation checks."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Hypno-Hub Validation Script{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = []
    
    # Check core application files
    print(f"\n{BLUE}Checking Core Application Files...{RESET}")
    results.append(check_file_exists("hub/launcher.py", "Flask launcher"))
    results.append(check_file_exists("hub/ai_llm.py", "AI/LLM integration"))
    results.append(check_file_exists("hub/personas.py", "Persona management"))
    results.append(check_file_exists("hub/start-hub.sh", "Session manager script (Linux)"))
    results.append(check_file_exists("hub/start-hub.ps1", "Session manager script (Windows)"))
    results.append(check_file_exists("hub/consent.html", "Consent page"))
    results.append(check_file_exists("hub/configure.html", "Configuration page"))
    
    # Check Python syntax
    print(f"\n{BLUE}Checking Python Syntax...{RESET}")
    results.append(check_python_syntax("hub/launcher.py"))
    results.append(check_python_syntax("hub/ai_llm.py"))
    results.append(check_python_syntax("hub/personas.py"))
    
    # Check Docker files
    print(f"\n{BLUE}Checking Docker Configuration...{RESET}")
    results.append(check_docker_file())
    results.append(check_docker_compose())
    
    # Check directory structure
    print(f"\n{BLUE}Checking Directory Structure...{RESET}")
    results.append(check_directory_exists("hub", "Hub directory"))
    results.append(check_directory_exists("hub/scripts", "Scripts directory"))
    results.append(check_directory_exists("hub/logs", "Logs directory"))
    results.append(check_media_directories())
    
    # Check documentation
    print(f"\n{BLUE}Checking Documentation...{RESET}")
    results.append(check_file_exists("README.md", "README"))
    results.append(check_file_exists("SETUP.md", "Setup guide"))
    results.append(check_file_exists("WINDOWS-SETUP.md", "Windows setup guide"))
    results.append(check_file_exists("IMPLEMENTATION.md", "Implementation summary"))
    results.append(check_file_exists("UNCENSORED-MODELS.md", "Uncensored models guide"))
    results.append(check_file_exists("TESTING.md", "Testing guide"))
    
    # Check configuration files
    print(f"\n{BLUE}Checking Configuration Files...{RESET}")
    results.append(check_file_exists(".env.example", "Environment template"))
    results.append(check_file_exists(".gitignore", "Git ignore file"))
    results.append(check_file_exists("requirements.txt", "Requirements file"))
    results.append(check_file_exists("LICENSE", "License file"))
    results.append(check_file_exists("docker-compose.windows.yml", "Windows Docker Compose"))
    results.append(check_file_exists("windows-setup.ps1", "Windows setup script"))
    results.append(check_file_exists("ubuntu-setup.sh", "Ubuntu setup script"))
    
    # Check test files
    print(f"\n{BLUE}Checking Test Files...{RESET}")
    results.append(check_file_exists("test_personas.py", "Persona tests"))
    results.append(check_file_exists("test_ai_llm.py", "AI/LLM tests"))
    results.append(check_file_exists("test_launcher.py", "Launcher tests"))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    passed = sum(1 for r in results if r)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✓ All checks passed! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}Your Hypno-Hub installation is ready!{RESET}")
        print(f"\nNext steps:")
        print(f"  1. Add media files to hub/media/ directories")
        print(f"  2. Install Ollama and pull models")
        print(f"  3. Run: docker compose up -d")
        print(f"  4. Access: http://localhost:9999")
        return 0
    elif percentage >= 75:
        print(f"{YELLOW}⚠ Most checks passed ({passed}/{total} - {percentage:.0f}%){RESET}")
        print(f"\n{YELLOW}Some non-critical issues found. Review warnings above.{RESET}")
        return 1
    else:
        print(f"{RED}✗ Multiple checks failed ({passed}/{total} - {percentage:.0f}%){RESET}")
        print(f"\n{RED}Please fix the errors above before proceeding.{RESET}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
