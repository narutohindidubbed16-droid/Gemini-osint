import os
import fcntl
import sys
import os
import asyncio
import logging
import nest_asyncio
import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Import the keep_alive function
try:
    from keep_alive import keep_alive 
except ImportError:
    # This error occurred in your logs (22135.jpg)
    print("FATAL ERROR: Could not import 'keep_alive.py'.")
    print("Ensure the file exists in the same directory and your Render Start Command is 'python main.py'")
    sys.exit(1)


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
    """Initializes and runs the Telegram Bot in Polling Mode using manual loop control."""
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    
    # --- Start Polling using manual lifecycle methods (FIX FOR THE ERROR) ---
    try:
        logger.info("✅ Bot Application starting...")
        
        # 1. Start the application (sets up the polling loop)
        await app.initialize()
        await app.start()
        
        logger.info("✅ Polling loop successfully started. Main thread waiting indefinitely.")
        
        # 2. Keep the main loop running indefinitely. This simulates app.run_polling()
        # but avoids the problematic cleanup/shutdown code that caused the error.
        await asyncio.Future() # Wait forever
        
    except asyncio.CancelledError:
        # Expected when the loop is cancelled/shut down
        logger.info("Asyncio loop cancelled. Stopping bot application...")
    except Exception as e:
        logger.error(f"Polling loop failed: {e}")
    finally:
        # Ensure the application stops gracefully on exit
        if app.running:
            await app.stop()
        logger.info("Bot application stopped gracefully.")


# ---------------------------------------------------
# ENTRY POINT (The Final Orchestration)
# ---------------------------------------------------
if __name__ == '__main__':
    # 1. Apply the patch immediately at the start of the main execution.
    logger.info("Applying nest_asyncio patch...")
    nest_asyncio.apply()
    
    # 2. Start the Flask keep-alive server in a background thread.
    keep_alive()
    
    # 3. Run the Bot Polling loop in the main thread.
    logger.info("Starting Bot Asyncio Loop...")
    try:
        # The main thread runs the bot's asynchronous loop.
        # This will now run the robust 'run_bot' logic above.
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Fatal error during asyncio run: {e}")
        
