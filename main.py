import os
import asyncio
import logging
import threading
import nest_asyncio
from flask import Flask
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes # Include ContextTypes for type hinting
)
from telegram import Update # Include Update for type hinting

# --- Configuration and Environment Setup ---
# Set the port Render provides
PORT = int(os.environ.get('PORT', 8080))
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flask App for UptimeRobot ---
app_flask = Flask(__name__)

@app_flask.route('/', methods=['GET', 'HEAD'])
def alive_check():
    """Simple route to keep the Render service alive."""
    return "OK", 200

# --- Telegram Bot Logic (Simplified Placeholder) ---

# Dummy handlers for the application structure
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder start command handler."""
    await update.message.reply_text("Hello! Bot is running in Polling Mode (via Render Web Service).")

# You must add your actual handlers (like process_text, buttons, etc.) here or import them:
# Example:
# from handlers import process_text, buttons
# ...

async def start_bot_polling():
    """Initializes and runs the Telegram Bot in Polling Mode."""
    if not BOT_TOKEN:
        logger.error("FATAL: BOT_TOKEN environment variable is not set. Exiting.")
        os._exit(1)

    logger.info("🚀 Initializing Application Builder...")
    
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # --- Add Handlers ---
    app.add_handler(CommandHandler("start", start))
    # Add your real handlers here:
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    try:
        logger.info("✅ Bot Polling Thread Started. Running app.run_polling()...")
        # app.run_polling() blocks this thread indefinitely
        await app.run_polling(close_loop=True, stop_signals=None) 
    except Exception as e:
        logger.error(f"Polling loop failed: {e}")
    finally:
        logger.info("Polling loop finished or stopped.")


# --- Entry Point and Thread Management ---

def run_bot_in_thread():
    """Sets up nest_asyncio and runs the bot polling loop in its own asyncio loop."""
    try:
        # Patch the current loop to allow nesting, fixing the 'event loop already running' error
        nest_asyncio.apply()
        
        # Run the asynchronous bot function within its own loop
        asyncio.run(start_bot_polling())
    except Exception as e:
        logger.error(f"Error starting background bot thread: {e}")


if __name__ == '__main__':
    # 1. Start the bot polling loop in a background daemon thread.
    # Daemon=True ensures the thread is killed when the main Flask thread exits.
    bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
    bot_thread.start()
    
    logger.info("Background bot polling thread initialized.")

    # 2. Start the Flask server on the main thread (Render's requirement).
    # This keeps the Render Web Service alive and responsive to UptimeRobot pings.
    logger.info(f"Starting Flask web server on port {PORT} for keep-alive route...")
    
    # We use app_flask.run() to start the server.
    # The debug=False is crucial for production stability.
    app_flask.run(host='0.0.0.0', port=PORT, debug=False)
    
