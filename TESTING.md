# Testing Guide for Hypno-Hub

This document describes how to test the Hypno-Hub application.

## Quick Start

### Running Unit Tests

```bash
# Run all tests
python3 test_personas.py
python3 test_ai_llm.py

# Or if you have pytest installed
pytest test_*.py -v
```

### Running Integration Tests

Integration tests require Flask to be installed:

```bash
# Install test dependencies
pip3 install flask requests

# Run launcher tests
python3 test_launcher.py
```

## Test Coverage

### Persona Tests (`test_personas.py`)

Tests the persona management system including:
- Persona retrieval and validation
- Kink zone configuration
- Safety level settings
- Data integrity checks
- Safety logic validation

**Run:** `python3 test_personas.py`

**Expected:** 16 tests pass

### AI/LLM Tests (`test_ai_llm.py`)

Tests the Ollama integration including:
- Client initialization
- Connection checking
- Model listing
- Script generation
- Prompt building
- Content filtering

**Run:** `python3 test_ai_llm.py`

**Expected:** 11 tests pass

**Note:** These tests use mocks and don't require a real Ollama server.

### Launcher Tests (`test_launcher.py`)

Tests the Flask web application including:
- Route handling
- API endpoints
- Session management
- Error handling

**Run:** `python3 test_launcher.py`

**Requires:** Flask installed (`pip3 install flask`)

## Manual Testing

### Health Check

```bash
# Start the service
docker compose up -d

# Check health
curl http://localhost:9999/health

# Expected output:
# {"status":"healthy","service":"hypno-hub","version":"1.0.0"}
```

### API Endpoints

```bash
# List available personas
curl http://localhost:9999/api/personas

# List kink zones
curl http://localhost:9999/api/kink-zones

# List available models
curl http://localhost:9999/api/models

# Stop session
curl -X POST http://localhost:9999/api/stop
```

### Testing Ollama Integration

```bash
# Check Ollama is running on host
curl http://localhost:11434/api/tags

# Test from inside container
docker compose exec hypno-hub curl http://host.docker.internal:11434/api/tags

# Generate test script
docker compose exec hypno-hub python3 /home/beta/hub/ai_llm.py
```

### Testing Media Playback

```bash
# Add test media files
mkdir -p hub/media/{video,img,audio}

# Add some test files (replace with your own)
cp /path/to/video.mp4 hub/media/video/
cp /path/to/image.jpg hub/media/img/
cp /path/to/audio.mp3 hub/media/audio/

# Start a session via web interface
# Navigate to http://localhost:9999
# Click "I Consent - Enter"
# Verify media plays correctly
```

## Docker Testing

### Build Test

```bash
# Build the image
docker compose build

# Check for errors
docker compose config
```

### Container Test

```bash
# Start container
docker compose up -d

# Check logs
docker compose logs -f hypno-hub

# Check GPU access (if applicable)
docker compose exec hypno-hub ls -l /dev/dri

# Verify Python packages
docker compose exec hypno-hub pip3 list
```

### Resource Usage

```bash
# Monitor container resources
docker stats hypno-hub

# Check memory usage
docker compose exec hypno-hub free -h
```

## Testing Safety Features

### Emergency Exit Test

1. Configure i3 window manager with kill-switch:
   ```bash
   cat config/i3-config-snippet.conf >> ~/.config/i3/config
   i3-msg reload
   ```

2. Start a session
3. Press `Alt+Shift+E`
4. Verify all media stops immediately

### Content Filter Test

Generate scripts with different safety levels and verify appropriate content:

```python
from hub.ai_llm import OllamaClient

client = OllamaClient()

# Maximum safety
result = client.generate_script(
    persona="gentle_guide",
    duration=15,
    safety_level=5
)

# Minimal safety
result = client.generate_script(
    persona="bimbo_coach",
    duration=15,
    safety_level=1
)

# Verify both scripts have emergency exits and awakening sequences
```

## Common Issues

### Tests Fail with "No module named 'flask'"

```bash
pip3 install flask requests
```

### Tests Fail with Permission Error

The tests create temporary directories. If you see permission errors:

```bash
# Make sure you have write access to /tmp
ls -ld /tmp

# Or run tests from a directory you own
cd ~/hypno-hub-test
python3 /path/to/test_*.py
```

### Ollama Connection Fails in Tests

The unit tests mock Ollama and don't require a real connection. Integration tests that need Ollama will skip if it's not available.

```bash
# Check Ollama is running
ollama list

# Start Ollama if needed
ollama serve
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests that don't require external services
python3 test_personas.py
python3 test_ai_llm.py

# Install dependencies for launcher tests
pip3 install flask requests
python3 test_launcher.py
```

## Test Data

Test data is stored in:
- `/tmp/` - Temporary test files (automatically cleaned up)
- `hub/scripts/` - Generated scripts (can be reviewed manually)
- `hub/logs/` - Session and error logs

## Adding New Tests

When adding new features, add corresponding tests:

1. **Unit tests**: Test individual functions in isolation
2. **Integration tests**: Test how components work together
3. **Manual tests**: Document how to manually verify the feature

Example test structure:

```python
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_feature_works(self):
        """Test that the feature works as expected."""
        # Arrange
        # Act
        # Assert
        pass

if __name__ == "__main__":
    unittest.main()
```

## Test Best Practices

1. **Isolate tests**: Each test should be independent
2. **Use mocks**: Mock external dependencies (Ollama, file system)
3. **Test edge cases**: Test both success and failure scenarios
4. **Clean up**: Always clean up test data in tearDown()
5. **Document**: Add docstrings explaining what each test does

## Reporting Issues

When reporting test failures, include:

1. Test command that failed
2. Full error output
3. System information (OS, Python version)
4. Docker version (if applicable)
5. Ollama version (if applicable)

Example:

```bash
# System info
lsb_release -a
python3 --version
docker --version

# Run failing test with verbose output
python3 test_personas.py -v 2>&1 | tee test_output.log
```

## Performance Testing

For performance testing:

```bash
# Time script generation
time docker compose exec hypno-hub python3 -c "
from hub.ai_llm import OllamaClient
client = OllamaClient()
client.generate_script(persona='gentle_guide', duration=20)
"

# Monitor GPU usage during generation
watch -n1 rocm-smi  # For AMD GPUs
# or
watch -n1 nvidia-smi  # For NVIDIA GPUs
```

## Security Testing

Verify security features:

1. **Non-root user**: Container runs as non-root
   ```bash
   docker compose exec hypno-hub whoami
   # Should output: hypnouser
   ```

2. **Dropped capabilities**: Container has minimal capabilities
   ```bash
   docker compose exec hypno-hub cat /proc/1/status | grep Cap
   ```

3. **No secrets in logs**: Check logs don't contain sensitive data
   ```bash
   docker compose logs hypno-hub | grep -i "password\|secret\|key"
   ```

## Conclusion

Regular testing ensures the Hypno-Hub application remains stable, secure, and functional. Run tests before committing changes and after pulling updates.

For questions or issues with testing, please open an issue on GitHub.
