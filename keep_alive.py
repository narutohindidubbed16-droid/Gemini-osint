import os
import threading
from flask import Flask
import logging
import sys

# --- Setup Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Ensure handlers are present if this file is run directly
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- Flask App Configuration ---
# Get the port Render provides
PORT = int(os.environ.get('PORT', 8080))
app_flask = Flask(__name__)

@app_flask.route('/', methods=['GET', 'HEAD'])
def alive_check():
    """Simple route to satisfy Render's requirement and UptimeRobot."""
    return "OK", 200

def run_flask_server():
    """Function to run the Flask server."""
    try:
        # Crucial: use_reloader=False prevents Flask from running twice, which can cause issues.
        logger.info(f"Flask Server: Starting keep-alive server on port {PORT}...")
        # Note: Render often overrides the port to 10000, which is normal.
        app_flask.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask Server: Failed to start server: {e}")

def keep_alive():
    """Exposed function to start the Flask server in a background daemon thread."""
    # Start the server in a separate daemon thread
    t = threading.Thread(target=run_flask_server, daemon=True)
    t.start()
    logger.info("Flask Server: Keep-alive thread started successfully.")

if __name__ == '__main__':
    # This block is for local testing and should not run on Render deployment
    logger.warning("Running keep_alive.py directly. This is usually only for local testing.")
    run_flask_server()
