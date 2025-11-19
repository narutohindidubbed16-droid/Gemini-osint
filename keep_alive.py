import os
import threading
import logging
import sys
from flask import Flask
from waitress import serve  # PRODUCTION WSGI SERVER (NO DUPLICATES)

# ------------------------------------------
# Logging Setup
# ------------------------------------------
logger = logging.getLogger("keep_alive")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ------------------------------------------
# Flask App
# ------------------------------------------
PORT = int(os.environ.get("PORT", 8080))
app_flask = Flask(__name__)

@app_flask.route("/", methods=["GET", "HEAD"])
def alive():
    return "OK", 200

# ------------------------------------------
# Waitress Server (NO RELOADER, NO DUPLICATE)
# ------------------------------------------
def run_flask_server():
    try:
        logger.info(f"[KeepAlive] Starting Waitress server on port {PORT}…")
        serve(app_flask, host="0.0.0.0", port=PORT)
    except Exception as e:
        logger.error(f"[KeepAlive] Failed to start server: {e}")

# ------------------------------------------
# Start Server in Background Thread
# ------------------------------------------
def keep_alive():
    t = threading.Thread(target=run_flask_server, daemon=True)
    t.start()
    logger.info("[KeepAlive] Keep-alive thread started successfully.")
