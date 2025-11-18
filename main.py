import os
import logging
import threading
from flask import Flask
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
import asyncio

from config import BOT_TOKEN
from handlers import start, verify_join, buttons, process_text

# ------------------ Logging ------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ------------------ Flask App ------------------
flask_app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))

@flask_app.route("/")
def home():
    return "Bot + Flask running on Render ✔"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, threaded=True)


# ------------------ BOT FUNCTION ------------------
async def run_bot():
    logger.info("🚀 Starting Nagi OSINT PRO (Polling Mode)...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    logger.info("🤖 Bot is LIVE (Polling Mode)…")
    await app.run_polling()


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    # Start Flask in background thread
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Flask started in background thread.")

    # Start Bot in MAIN THREAD (IMPORTANT!)
    asyncio.run(run_bot())
