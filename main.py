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

try:
    from keep_alive import keep_alive
except ImportError:
    print("FATAL ERROR: Could not import 'keep_alive.py'.")
    sys.exit(1)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Bot is alive and polling.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")


async def run_bot():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        os._exit(1)

    logger.info("🚀 Initializing Application Builder...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    try:
        logger.info("Starting bot...")

        await app.initialize()
        await app.start()      # PTB v20+ auto-starts polling here

        logger.info("✅ Bot is ONLINE & POLLING.")
        await asyncio.Future()  # keep alive

    except Exception as e:
        logger.error(f"ERROR: {e}")
    finally:
        await app.stop()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    logger.info("Applying nest_asyncio patch...")
    nest_asyncio.apply()

    keep_alive()

    logger.info("Starting bot loop...")
    asyncio.run(run_bot())
