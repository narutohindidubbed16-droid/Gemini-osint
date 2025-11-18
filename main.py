import os
import logging
import threading
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from flask import Flask

# --- Imports from your project ---
from config import BOT_TOKEN
from handlers import (
    start,
    verify_join,
    buttons,
    process_text
)

# --- Configuration ---
PORT = int(os.environ.get('PORT', 8080))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)

# Define the bot's core polling loop function
async def start_bot_polling():
    logger.info("🚀 Starting Nagi OSINT PRO in Polling Mode (Threaded)...")
    
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # --- Handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    logger.info("✅ Bot Polling Thread Started.")
    # Run polling, which will block this thread
    await app.run_polling(close_loop=False)

# Flask route to satisfy Render's Web Service requirement
@app_flask.route('/')
def home():
    return "Bot is running in a background thread."

# Function to start the bot thread
def run_bot_thread():
    # We run the polling function in a new thread
    bot_thread = threading.Thread(target=lambda: asyncio.run(start_bot_polling()))
    bot_thread.start()
    logger.info("Background bot thread initialized.")

if __name__ == '__main__':
    import asyncio
    
    # 1. Start the bot in a background thread
    run_bot_thread()
    
    # 2. Start the Flask server on the main thread
    # This keeps the main process alive, satisfying the Render Web Service requirements.
    logger.info(f"Starting Flask web server on port {PORT}...")
    app_flask.run(host='0.0.0.0', port=PORT, threaded=True)
    
