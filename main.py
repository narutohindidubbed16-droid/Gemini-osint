import os
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN
from handlers import start, verify_join, buttons, process_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def run_bot():
    logger.info("🚀 Starting Nagi OSINT PRO in Polling Mode...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # PTB handles async internally
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    logger.info("✅ Bot is LIVE & Running (POLLING MODE)…")

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
