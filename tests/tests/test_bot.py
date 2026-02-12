# tests/test_bot.py
import pytest
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from app.handlers import start_command, help_command, handle_bot_message

@pytest.mark.asyncio
async def test_start_authorized(monkeypatch):
    # Mock settings
    monkeypatch.setattr("app.config.settings.ALLOWED_USER_IDS", [12345])

    user = User(id=12345, first_name="Test", is_bot=False)
    chat = Chat(id=1, type="private")
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/start")
    update = Update(update_id=1, message=message)
    context = ContextTypes.DEFAULT_TYPE()

    await start_command(update, context)
    assert "✅ Welcome!" in update.message.reply_text.call_args[0][0]
