#!/usr/bin/env python3
"""
Hypno Hub Launcher
Flask web server for the consent page and session management.
"""

from flask import Flask, render_template_string, request, redirect, jsonify
import subprocess
import os
import sys
import logging
import platform

# Import AI and persona modules
try:
    from ai_llm import OllamaClient
    from personas import list_personas, list_kink_zones, list_models
except ImportError:
    OllamaClient = None
    def list_personas(): return []
    def list_kink_zones(): return []
    def list_models(): return []

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get the HTML templates
CONSENT_HTML_PATH = '/home/beta/hub/consent.html'
CONFIGURE_HTML_PATH = '/home/beta/hub/configure.html'

try:
    with open(CONSENT_HTML_PATH, 'r') as f:
        consent_template = f.read()
except FileNotFoundError:
    logger.error(f"Consent HTML file not found at {CONSENT_HTML_PATH}")
    consent_template = "<h1>Error: Consent page not found</h1>"

try:
    with open(CONFIGURE_HTML_PATH, 'r') as f:
        configure_template = f.read()
except FileNotFoundError:
    logger.warning(f"Configure HTML file not found at {CONFIGURE_HTML_PATH}")
    configure_template = None


@app.route('/')
def index():
    """Serve the consent page."""
    return render_template_string(consent_template)


@app.route('/configure')
def configure():
    """Serve the persona/kink configuration page."""
    if configure_template:
        return render_template_string(configure_template)
    else:
        return redirect('/start')


@app.route('/configure', methods=['POST'])
def configure_session():
    """Handle configuration form submission and generate AI script."""
    try:
        # Get form data with validation
        persona = request.form.get('persona', 'gentle_guide')
        kink_zones = request.form.get('kink_zone', 'relaxation').split(',')
        model = request.form.get('model', 'dolphin-llama3:8b')
        
        # Validate and parse safety level (1-5)
        try:
            safety_level = int(request.form.get('safety_level', 3))
            if not 1 <= safety_level <= 5:
                logger.warning(f"Invalid safety level {safety_level}, using default 3")
                safety_level = 3
        except (ValueError, TypeError):
            logger.warning("Invalid safety level format, using default 3")
            safety_level = 3
        
        # Validate and parse duration (5-120 minutes)
        try:
            duration = int(request.form.get('duration', 20))
            if not 5 <= duration <= 120:
                logger.warning(f"Invalid duration {duration}, using default 20")
                duration = 20
        except (ValueError, TypeError):
            logger.warning("Invalid duration format, using default 20")
            duration = 20
        
        logger.info(f"Generating script: persona={persona}, zones={kink_zones}, "
                   f"model={model}, safety={safety_level}, duration={duration}")
        
        # Generate AI script if OllamaClient is available
        if OllamaClient:
            client = OllamaClient()
            
            # Generate script with first kink zone
            kink_zone = kink_zones[0] if kink_zones else None
            result = client.generate_script(
                persona=persona,
                duration=duration,
                kink_zone=kink_zone,
                model=model,
                safety_level=safety_level
            )
            
            if "error" in result:
                logger.error(f"Script generation failed: {result['error']}")
                return f"Error generating script: {result['error']}", 500
            
            logger.info(f"Script generated successfully: {result.get('timestamp', 'unknown')}")
        else:
            logger.warning("OllamaClient not available, skipping script generation")
        
        # Redirect to start session
        return redirect('/start_configured')
        
    except Exception as e:
        logger.error(f"Error in configure_session: {e}")
        return f"Error: {e}", 500


@app.route('/start_configured', methods=['GET', 'POST'])
def start_configured():
    """Start session after configuration."""
    return start()


@app.route('/start', methods=['POST'])
def start():
    """Start the hypno session after consent."""
    try:
        logger.info("User consented - starting session")
        
        # Determine the appropriate script based on platform
        if platform.system() == 'Windows':
            script_path = '/home/beta/hub/start-hub.ps1'
            script_cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path]
        else:
            script_path = '/home/beta/hub/start-hub.sh'
            script_cmd = ['/bin/bash', script_path]
        
        if os.path.exists(script_path):
            subprocess.Popen(script_cmd)
            logger.info("Session started successfully")
        else:
            logger.error(f"Start script not found at {script_path}")
            return "Error: Start script not found", 500
        
        # Return a blank page while the session starts
        return redirect('/session')
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        return f"Error starting session: {e}", 500


@app.route('/session')
def session():
    """Display session active page."""
    return """
    <!doctype html>
    <html>
    <head>
        <title>Session Active</title>
        <style>
            body {
                background: #000;
                color: #0f0;
                font-family: monospace;
                text-align: center;
                margin-top: 20%;
            }
            h1 { font-size: 2em; }
            .info { margin: 2em; color: #0ff; }
            kbd {
                background: #333;
                padding: 0.3em 0.6em;
                border-radius: 3px;
                border: 1px solid #0f0;
            }
        </style>
    </head>
    <body>
        <h1>🌀 Session Active 🌀</h1>
        <div class="info">
            <p>Your session is now running.</p>
            <p>Press <kbd>Alt+Shift+E</kbd> to exit at any time.</p>
            <p><a href="/" style="color: #0ff;">Return to Start</a></p>
        </div>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'hypno-hub',
        'version': '1.0.0'
    })


@app.route('/api/stop', methods=['POST'])
def stop():
    """API endpoint to stop the session."""
    try:
        if platform.system() == 'Windows':
            # On Windows, use taskkill to stop processes
            subprocess.run(['taskkill', '/F', '/IM', 'mpv.exe'], check=False, 
                          stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'feh.exe'], check=False,
                          stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:
            # On Unix-like systems, use pkill
            subprocess.run(['pkill', '-f', 'mpv'], check=False)
            subprocess.run(['pkill', '-f', 'feh'], check=False)
        logger.info("Session stopped via API")
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping session: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/personas')
def api_personas():
    """API endpoint to get available personas."""
    return jsonify(list_personas())


@app.route('/api/kink-zones')
def api_kink_zones():
    """API endpoint to get available kink zones."""
    return jsonify(list_kink_zones())


@app.route('/api/models')
def api_models():
    """API endpoint to get available AI models."""
    return jsonify(list_models())


if __name__ == '__main__':
    logger.info("Starting Hypno Hub on port 9999")
    logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')}")
    
    app.run(
        host='0.0.0.0',
        port=9999,
        debug=False
    )
