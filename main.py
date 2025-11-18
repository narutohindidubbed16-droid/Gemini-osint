import os
import asyncio
import logging
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# Import the keep_alive function from the separate file
from keep_alive import keep_alive 

# --- Configuration and Environment Setup ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Telegram Bot Handlers (Adjust these as needed) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The /start command handler."""
    await update.message.reply_text("👋 Hello! Bot is alive and polling.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder handler to echo user messages."""
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

# --- Bot Core Logic ---

async def run_bot():
    """Initializes and runs the Telegram Bot in Polling Mode."""
    if not BOT_TOKEN:
        logger.error("FATAL: BOT_TOKEN environment variable is not set. Cannot start bot.")
        os._exit(1)

    logger.info("🚀 Initializing Application Builder...")
    
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # --- Add Handlers (Customize this block) ---
    app.add_handler(CommandHandler("start", start))
    # Add your message and callback handlers here:
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    
    # --- Start Polling ---
    try:
        logger.info("✅ Bot Polling starting in Main Thread...")
        # Polling runs in the main thread (managed by asyncio.run below)
        await app.run_polling(close_loop=True, stop_signals=None) 
    except Exception as e:
        logger.error(f"Polling loop failed: {e}")


# ---------------------------------------------------
# ENTRY POINT (The Final Orchestration)
# ---------------------------------------------------
if __name__ == '__main__':
    # 1. Start the Flask keep-alive server in a background thread.
    keep_alive()
    
    # 2. Apply the patch to allow the Polling loop to run without conflict.
    # This is the fix for the "event loop already running" error.
    nest_asyncio.apply()
    
    # 3. Run the Bot Polling loop in the main thread.
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Fatal error during asyncio run: {e}")
        
