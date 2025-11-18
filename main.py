import os
import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN
from handlers import (
    start,
    verify_join,
    buttons,
    process_text
)

# --- Configuration for Webhook ---
PORT = int(os.environ.get('PORT', 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 
# IMPORTANT: Polling mode logic is completely removed.

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_bot():
    # If the bot token or webhook URL is missing, it will crash immediately
    if not BOT_TOKEN or not WEBHOOK_URL:
        logger.error("CRITICAL: BOT_TOKEN or WEBHOOK_URL is missing from environment variables.")
        return

    logger.info("🚀 Starting Nagi OSINT PRO in WEBHOOK Mode...")
    
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

    # --- Start Webhook ---
    try:
        full_webhook_url = WEBHOOK_URL + "/" + BOT_TOKEN # Using the token as path
        await app.bot.set_webhook(url=full_webhook_url)
        logger.info(f"✅ Webhook set to: {full_webhook_url}")
        
        # Start the web server and block forever
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN, 
            webhook_url=full_webhook_url
        )
        logger.info(f"✅ Bot is LIVE & Running on port {PORT} (WEBHOOK)…")
    except Exception as e:
        logger.error(f"CRITICAL WEBHOOK ERROR: {e}")

# ---------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------
if __name__ == "__main__":
    try:
        # Use asyncio.run for the simple entry point
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        
