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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get the consent HTML template
CONSENT_HTML_PATH = '/home/beta/hub/consent.html'

try:
    with open(CONSENT_HTML_PATH, 'r') as f:
        consent_template = f.read()
except FileNotFoundError:
    logger.error(f"Consent HTML file not found at {CONSENT_HTML_PATH}")
    consent_template = "<h1>Error: Consent page not found</h1>"


@app.route('/')
def index():
    """Serve the consent page."""
    return render_template_string(consent_template)


@app.route('/start', methods=['POST'])
def start():
    """Start the hypno session after consent."""
    try:
        logger.info("User consented - starting session")
        
        # Start the hub in the background
        script_path = '/home/beta/hub/start-hub.sh'
        
        if os.path.exists(script_path):
            subprocess.Popen(['/bin/bash', script_path])
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
        subprocess.run(['pkill', '-f', 'mpv'], check=False)
        subprocess.run(['pkill', '-f', 'feh'], check=False)
        logger.info("Session stopped via API")
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping session: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Hypno Hub on port 9999")
    logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')}")
    
    app.run(
        host='0.0.0.0',
        port=9999,
        debug=False
    )
