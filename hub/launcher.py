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
import re
from datetime import datetime, timedelta

# Import AI and persona modules
try:
    from ai_llm import OllamaClient
    from personas import list_personas, list_kink_zones, list_models, PERSONAS, KINK_ZONES, UNCENSORED_MODELS
except ImportError:
    OllamaClient = None
    PERSONAS = {}
    KINK_ZONES = {}
    UNCENSORED_MODELS = {}
    def list_personas(): return []
    def list_kink_zones(): return []
    def list_models(): return []

# Import media downloader
try:
    from media_downloader import MediaDownloader
except ImportError:
    MediaDownloader = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security: Add secret key for session management
# In production, always set SECRET_KEY environment variable
import secrets
_DEFAULT_DEV_KEY = os.getenv('SECRET_KEY')
if not _DEFAULT_DEV_KEY:
    logger.warning("SECRET_KEY not set - using random key (sessions will not persist across restarts)")
    _DEFAULT_DEV_KEY = secrets.token_hex(32)
app.config['SECRET_KEY'] = _DEFAULT_DEV_KEY

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Note: Not adding CSP as it might interfere with inline scripts
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status': 500
    }), 500

@app.errorhandler(429)
def rate_limit_error(error):
    """Handle 429 rate limit errors."""
    return jsonify({
        'error': 'Too Many Requests',
        'message': 'Rate limit exceeded. Please try again later.',
        'status': 429
    }), 429

# Rate limiting state (simple in-memory)
_rate_limit_cache = {}

def check_rate_limit(key: str, limit: int = 10, window: int = 60) -> bool:
    """Simple rate limiting check."""
    now = datetime.now()
    if key not in _rate_limit_cache:
        _rate_limit_cache[key] = []
    
    # Clean old entries
    _rate_limit_cache[key] = [
        ts for ts in _rate_limit_cache[key] 
        if now - ts < timedelta(seconds=window)
    ]
    
    # Check limit
    if len(_rate_limit_cache[key]) >= limit:
        return False
    
    _rate_limit_cache[key].append(now)
    return True

def sanitize_input(value: str, pattern: str = r'^[a-zA-Z0-9_.-]+$') -> str:
    """Sanitize input to prevent injection attacks."""
    if not value or not isinstance(value, str):
        return ''
    
    # Remove any potentially dangerous characters
    value = value.strip()
    
    # Check against allowed pattern
    if not re.match(pattern, value):
        logger.warning(f"Input validation failed for value: {value}")
        return ''
    
    return value

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
        # Rate limiting
        client_ip = request.remote_addr
        if not check_rate_limit(f"configure_{client_ip}", limit=5, window=60):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({'error': 'Too many requests. Please wait a moment.'}), 429
        
        # Get and validate form data
        persona_raw = request.form.get('persona', 'gentle_guide')
        kink_zones_raw = request.form.get('kink_zone', 'relaxation')
        model_raw = request.form.get('model', 'dolphin-llama3:8b')
        
        # Sanitize and validate persona
        persona = sanitize_input(persona_raw, r'^[a-z_]+$')
        if not persona or persona not in PERSONAS:
            logger.warning(f"Invalid persona '{persona_raw}', using default")
            persona = 'gentle_guide'
        
        # Sanitize and validate kink zones
        kink_zones = []
        for zone in kink_zones_raw.split(','):
            zone = sanitize_input(zone.strip(), r'^[a-z_]+$')
            if zone and zone in KINK_ZONES:
                kink_zones.append(zone)
        
        if not kink_zones:
            kink_zones = ['relaxation']
        
        # Sanitize and validate model
        model = sanitize_input(model_raw, r'^[a-zA-Z0-9.:+-]+$')
        if not model or model not in UNCENSORED_MODELS:
            logger.warning(f"Invalid model '{model_raw}', using default")
            model = 'dolphin-llama3:8b'
        
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
            
            # Check Ollama connection first
            if not client.check_connection():
                error_msg = "Unable to connect to Ollama AI service. Please ensure Ollama is running."
                logger.error(error_msg)
                return jsonify({'error': error_msg, 'details': 'Check OLLAMA_HOST configuration'}), 503
            
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
                return jsonify({
                    'error': 'Failed to generate script',
                    'details': result['error']
                }), 500
            
            logger.info(f"Script generated successfully: {result.get('timestamp', 'unknown')}")
        else:
            logger.warning("OllamaClient not available, skipping script generation")
        
        # Redirect to start session
        return redirect('/start_configured')
        
    except Exception as e:
        logger.error(f"Error in configure_session: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@app.route('/start_configured', methods=['GET', 'POST'])
def start_configured():
    """Start session after configuration."""
    return start()


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


@app.route('/media')
def media_manager():
    """Serve the media manager page."""
    try:
        with open('/home/beta/hub/media.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Media Manager not found</h1>", 404


@app.route('/session')
def session():
    """Display session active page with status monitoring."""
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
                margin-top: 10%;
                padding: 2em;
            }
            h1 { 
                font-size: 2.5em; 
                text-shadow: 0 0 20px #0f0;
                animation: pulse 2s ease-in-out infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            .info { 
                margin: 2em auto; 
                color: #0ff; 
                max-width: 600px;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #0f0;
                animation: blink 1s ease-in-out infinite;
                margin-right: 0.5em;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            kbd {
                background: #333;
                padding: 0.3em 0.6em;
                border-radius: 3px;
                border: 1px solid #0f0;
                font-size: 1.1em;
            }
            a {
                color: #0ff;
                text-decoration: none;
                border: 1px solid #0ff;
                padding: 0.5em 1em;
                border-radius: 5px;
                display: inline-block;
                margin-top: 1em;
                transition: all 0.3s;
            }
            a:hover {
                background: rgba(0, 255, 255, 0.2);
                transform: scale(1.05);
            }
            .warning {
                color: #ff0;
                font-size: 1.2em;
                margin: 1.5em 0;
            }
        </style>
    </head>
    <body>
        <h1>🌀 Session Active 🌀</h1>
        <div class="info">
            <p><span class="status-indicator"></span><strong>Session is running</strong></p>
            <p class="warning">⚠️ Emergency Exit: Press <kbd>Alt+Shift+E</kbd> to stop immediately</p>
            <p>Your personalized hypnosis session is now playing.</p>
            <p>You can safely close this browser window.</p>
            <p><a href="/">← Return to Home</a></p>
            <p style="margin-top: 2em; font-size: 0.9em; color: #666;">
                To stop the session via API: <code style="color: #999;">curl -X POST http://localhost:9999/api/stop</code>
            </p>
        </div>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check endpoint with detailed status."""
    health_status = {
        'status': 'healthy',
        'service': 'hypno-hub',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }
    
    # Check Ollama connection
    if OllamaClient:
        try:
            client = OllamaClient()
            ollama_connected = client.check_connection()
            health_status['ollama'] = {
                'connected': ollama_connected,
                'host': client.host
            }
            if ollama_connected:
                try:
                    models = client.list_models()
                    health_status['ollama']['models_available'] = len(models)
                except:
                    health_status['ollama']['models_available'] = 0
        except Exception as e:
            health_status['ollama'] = {
                'connected': False,
                'error': str(e)
            }
    else:
        health_status['ollama'] = {'available': False}
    
    # Check file system
    try:
        scripts_dir = '/home/beta/hub/scripts'
        logs_dir = '/home/beta/hub/logs'
        media_dir = '/home/beta/hub/media'
        
        health_status['filesystem'] = {
            'scripts_writable': os.access(scripts_dir, os.W_OK) if os.path.exists(scripts_dir) else False,
            'logs_writable': os.access(logs_dir, os.W_OK) if os.path.exists(logs_dir) else False,
            'media_readable': os.access(media_dir, os.R_OK) if os.path.exists(media_dir) else False
        }
    except Exception as e:
        health_status['filesystem'] = {'error': str(e)}
    
    # Overall status
    overall_healthy = health_status.get('ollama', {}).get('connected', False)
    health_status['status'] = 'healthy' if overall_healthy else 'degraded'
    
    status_code = 200 if overall_healthy else 503
    return jsonify(health_status), status_code


@app.route('/api/status')
def api_status():
    """Get current system status."""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'service': 'hypno-hub',
            'version': '1.0.0'
        }
        
        # Check if session is running
        try:
            mpv_running = subprocess.run(
                ['pgrep', '-f', 'mpv'],
                capture_output=True,
                timeout=2
            ).returncode == 0
            
            feh_running = subprocess.run(
                ['pgrep', '-f', 'feh'],
                capture_output=True,
                timeout=2
            ).returncode == 0
            
            status['session_active'] = mpv_running or feh_running
        except:
            status['session_active'] = False
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': 'Failed to get status'}), 500


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


@app.route('/api/personas')
def api_personas():
    """API endpoint to get available personas."""
    try:
        personas = list_personas()
        return jsonify({
            'status': 'success',
            'data': personas,
            'count': len(personas)
        })
    except Exception as e:
        logger.error(f"Error retrieving personas: {e}")
        return jsonify({'error': 'Failed to retrieve personas'}), 500


@app.route('/api/kink-zones')
def api_kink_zones():
    """API endpoint to get available kink zones."""
    try:
        zones = list_kink_zones()
        return jsonify({
            'status': 'success',
            'data': zones,
            'count': len(zones)
        })
    except Exception as e:
        logger.error(f"Error retrieving kink zones: {e}")
        return jsonify({'error': 'Failed to retrieve kink zones'}), 500


@app.route('/api/models')
def api_models():
    """API endpoint to get available AI models."""
    try:
        models = list_models()
        return jsonify({
            'status': 'success',
            'data': models,
            'count': len(models)
        })
    except Exception as e:
        logger.error(f"Error retrieving models: {e}")
        return jsonify({'error': 'Failed to retrieve models'}), 500


@app.route('/api/media/stats')
def api_media_stats():
    """Get media statistics."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    try:
        downloader = MediaDownloader()
        stats = downloader.get_media_stats()
        files = downloader.list_media_files(include_info=True)
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'total_files': len(files),
            'total_size_mb': sum(f['size_mb'] for f in files)
        })
    except Exception as e:
        logger.error(f"Error getting media stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/download', methods=['POST'])
def api_media_download():
    """Download media from URLs."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    # Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(f"media_download_{client_ip}", limit=5, window=60):
        return jsonify({'error': 'Too many download requests'}), 429
    
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        media_type = data.get('type', 'image')
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        downloader = MediaDownloader()
        
        if media_type == 'image':
            result = downloader.download_images(urls)
        elif media_type == 'video':
            result = downloader.download_videos(urls)
        else:
            return jsonify({'error': 'Invalid media type'}), 400
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/search', methods=['POST'])
def api_media_search():
    """Search and download images from APIs."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    # Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(f"media_search_{client_ip}", limit=3, window=60):
        return jsonify({'error': 'Too many search requests'}), 429
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        count = min(int(data.get('count', 10)), 50)  # Max 50
        sources = data.get('sources', ['unsplash', 'pexels', 'pixabay'])
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        downloader = MediaDownloader()
        result = downloader.search_and_download_images(query, count, sources)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error searching media: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/list')
def api_media_list():
    """List all media files."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    try:
        media_type = request.args.get('type', 'all')
        include_info = request.args.get('info', 'false').lower() == 'true'
        
        downloader = MediaDownloader()
        files = downloader.list_media_files(media_type, include_info)
        
        return jsonify({
            'status': 'success',
            'type': media_type,
            'count': len(files),
            'files': files
        })
        
    except Exception as e:
        logger.error(f"Error listing media: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/optimize', methods=['POST'])
def api_media_optimize():
    """Optimize images."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    # Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(f"media_optimize_{client_ip}", limit=2, window=60):
        return jsonify({'error': 'Too many optimization requests'}), 429
    
    try:
        data = request.get_json() or {}
        max_dimension = int(data.get('max_dimension', 1920))
        quality = int(data.get('quality', 85))
        
        downloader = MediaDownloader()
        count = downloader.optimize_images(max_dimension, quality)
        
        return jsonify({
            'status': 'success',
            'optimized': count
        })
        
    except Exception as e:
        logger.error(f"Error optimizing media: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/thumbnails', methods=['POST'])
def api_media_thumbnails():
    """Generate video thumbnails."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    try:
        downloader = MediaDownloader()
        count = downloader.generate_thumbnails()
        
        return jsonify({
            'status': 'success',
            'generated': count
        })
        
    except Exception as e:
        logger.error(f"Error generating thumbnails: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/duplicates')
def api_media_duplicates():
    """Find duplicate files."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    try:
        downloader = MediaDownloader()
        duplicates = downloader.find_duplicates()
        
        return jsonify({
            'status': 'success',
            'duplicate_sets': len(duplicates),
            'duplicates': duplicates
        })
        
    except Exception as e:
        logger.error(f"Error finding duplicates: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/clear', methods=['POST'])
def api_media_clear():
    """Clear media files."""
    if not MediaDownloader:
        return jsonify({'error': 'MediaDownloader not available'}), 503
    
    # Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(f"media_clear_{client_ip}", limit=2, window=60):
        return jsonify({'error': 'Too many clear requests'}), 429
    
    try:
        data = request.get_json() or {}
        media_type = data.get('type', 'all')
        
        downloader = MediaDownloader()
        success = downloader.clear_media(media_type)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'cleared': media_type
        })
        
    except Exception as e:
        logger.error(f"Error clearing media: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Hypno Hub on port 9999")
    logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')}")
    
    # Initialize media downloader if available
    if MediaDownloader:
        try:
            downloader = MediaDownloader()
            stats = downloader.get_media_stats()
            logger.info(f"Media Library: {stats['images']['count']} images, "
                       f"{stats['videos']['count']} videos, "
                       f"{stats['audio']['count']} audio files")
        except Exception as e:
            logger.warning(f"Could not initialize MediaDownloader: {e}")
    
    app.run(
        host='0.0.0.0',
        port=9999,
        debug=False
    )
