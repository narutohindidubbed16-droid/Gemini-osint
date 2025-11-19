import os
import threading
import logging
import sys
from flask import Flask
from waitress import serve   # <--- IMPORTANT

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Flask App
PORT = int(os.environ.get('PORT', 8080))
app_flask = Flask(__name__)

@app_flask.route('/', methods=['GET', 'HEAD'])
def alive_check():
    return "OK", 200

def run_flask_server():
    """Run Flask via Waitress instead of werkzeug."""
    try:
        logger.info(f"[KeepAlive] Starting Waitress server on port {PORT}…")
        serve(app_flask, host="0.0.0.0", port=PORT)   # <--- SINGLE INSTANCE
    except Exception as e:
        logger.error(f"[KeepAlive] Failed to start keep-alive server: {e}")

def keep_alive():
    """Start the keep-alive server in a background daemon thread."""
    t = threading.Thread(target=run_flask_server, daemon=True)
    t.start()
    logger.info("[KeepAlive] Keep-alive thread started successfully.")
