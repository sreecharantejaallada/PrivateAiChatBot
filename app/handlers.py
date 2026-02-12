# app/handlers.py
import logging
from typing import Final

from telegram import Update
from telegram.ext import ContextTypes

from .config import settings
from .ollama import query_ollama
from .logger import get_logger

log = get_logger(__name__)

BOT_USERNAME: Final = settings.BOT_USERNAME
ALLOWED_USER_IDS = set(settings.ALLOWED_USER_IDS)

# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #
def _is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS

def _strip_bot_mention(text: str) -> str:
    """Remove the bot username from a group message."""
    return text.replace(BOT_USERNAME, "").strip()

# --------------------------------------------------------------------------- #
# Command handlers
# --------------------------------------------------------------------------- #
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_authorized(user.id):
        await update.message.reply_text(
            "🚫 Access restricted.\n\nPlease contact *Charan* to request access.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        "✅ Welcome!\n\nThis is a bot developed by Charan.\nHow can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/start – Initialise the bot\n"
        "/help – Show this help message\n"
        "/weather – Get weather (placeholder)"
    )

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please provide a city name to get the weather information.")

# --------------------------------------------------------------------------- #
# Message handler (core logic)
# --------------------------------------------------------------------------- #
async def handle_message(prompt: str, username: str) -> str:
    """Delegate to Ollama and return the response."""
    response = await query_ollama(prompt)
    return response

async def handle_bot_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user_id = update.effective_user.id
    chat_type = update.message.chat.type
    chat_username = update.message.chat.username or "unknown"
    text = update.message.text or ""

    log.info(
        "Incoming message",
        extra={"user_id": user_id, "chat_type": chat_type, "text": text},
    )

    if not _is_authorized(user_id):
        await update.message.reply_text(
            "🚫 Access restricted.\n\nPlease contact Charan for access."
        )
        return

    # Group handling – reply only when mentioned
    if chat_type == "group":
        if BOT_USERNAME not in text:
            return
        text = _strip_bot_mention(text)

    try:
        response = await handle_message(text, chat_username)
        log.info("Bot reply", extra={"reply": response})
        await update.message.reply_text(response)
    except Exception as exc:
        log.exception("Failed to process message")
        await update.message.reply_text("⚠️ An internal error occurred. Please try again later.")

# --------------------------------------------------------------------------- #
# Global error handler
# --------------------------------------------------------------------------- #
async def global_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error(
        "Unhandled exception",
        exc_info=context.error,
        extra={"update": str(update)},
    )
    # Optional: send alert to monitoring channel / Slack / Sentry etc.
