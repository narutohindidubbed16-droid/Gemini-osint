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
# Fallback to Polling for local testing if WEBHOOK_URL is not set
POLLING_MODE = WEBHOOK_URL is None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_bot():
    logger.info("🚀 Starting Nagi OSINT PRO...")
    
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

    if not POLLING_MODE:
        # --- Start Webhook (for Render) ---
        try:
            full_webhook_url = WEBHOOK_URL + BOT_TOKEN
            await app.bot.set_webhook(url=full_webhook_url)
            logger.info(f"✅ Webhook set to: {full_webhook_url}")
            
            # Start the web server
            await app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN, 
                webhook_url=full_webhook_url
            )
            logger.info(f"✅ Bot is LIVE & Running on port {PORT} (WEBHOOK)…")
        except Exception as e:
            logger.error(f"CRITICAL WEBHOOK ERROR: {e}")
            
    else:
        # --- Fallback to Polling (for local dev) ---
        logger.warning("⚠️ WEBHOOK_URL not set. Running in Polling mode...")
        await app.run_polling(close_loop=False)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except RuntimeError:
        # For systems (like some IDEs) that already have a running loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
      
