import os
import threading
from flask import Flask
import logging

# Setup logging specific to the keep_alive module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        # We run Flask with threaded=True, listening on 0.0.0.0
        logger.info(f"Starting Flask keep-alive server on port {PORT}...")
        app_flask.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server failed to start: {e}")

def keep_alive():
    """Exposed function to start the Flask server in a background thread."""
    # Start the server in a separate daemon thread
    t = threading.Thread(target=run_flask_server, daemon=True)
    t.start()
    logger.info("Keep-alive thread started successfully.")

if __name__ == '__main__':
    # If this file is run directly, start the server normally (for testing)
    run_flask_server()
  
