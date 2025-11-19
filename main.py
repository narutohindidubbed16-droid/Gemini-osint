import os
import asyncio
import logging
import nest_asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Import keep-alive server
from keep_alive import keep_alive

# Import your handlers
from handlers import (
    start,
    verify_join,
    buttons,
    process_text
)

# Enable nest_asyncio
nest_asyncio.apply()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("FATAL ERROR ❌ — BOT_TOKEN is missing from Environment Variables.")


# -------------------------
# MAIN BOT RUNNER
# -------------------------
async def run_bot():
    logger.info("🚀 Initializing Application...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # -------------------------
    # Add All Handlers
    # -------------------------
    app.add_handler(CommandHandler("start", start))

    # Callback button handler
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
    app.add_handler(CallbackQueryHandler(buttons))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    # -------------------------
    # Start Polling Manually (stable)
    # -------------------------
    await app.initialize()
    await app.start()

    logger.info("✅ Polling Started — Bot is online!")

    await asyncio.Future()   # Keep alive forever


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    logger.info("🔄 Applying nest_asyncio & Starting keep-alive server...")
    keep_alive()  # Start Waitress server (Render requirement)

    logger.info("🤖 Starting bot event loop...")

    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"❌ FATAL ERROR in main asyncio loop: {e}")
