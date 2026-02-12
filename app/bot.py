# app/bot.py
import asyncio
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .config import settings
from .handlers import (
    start_command,
    help_command,
    weather_command,
    handle_bot_message,
    global_error,
)
from .logger import get_logger

log = get_logger(__name__)

def _build_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather_command))

    # Register generic text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_message))

    # Global error handler
    app.add_error_handler(global_error)

    return app

async def _run_polling(app: Application) -> None:
    log.info("Starting polling loop")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(poll_interval=3)
    # Keep running until a termination signal arrives
    await asyncio.Event().wait()

async def _run_webhook(app: Application) -> None:
    if not settings.WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL must be set when USE_WEBHOOK=True")
    log.info("Setting webhook to %s", settings.WEBHOOK_URL)
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(listen="0.0.0.0", port=8443, url_path=settings.TELEGRAM_TOKEN)
    await app.updater.bot.set_webhook(url=settings.WEBHOOK_URL)

def _setup_signal_handlers(app: Application) -> None:
    loop = asyncio.get_event_loop()

    async def _shutdown():
        log.info("Shutting down gracefully")
        await app.shutdown()
        await app.stop()
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

def main() -> None:
    app = _build_application()
    _setup_signal_handlers(app)

    if settings.USE_WEBHOOK:
        asyncio.run(_run_webhook(app))
    else:
        asyncio.run(_run_polling(app))

if __name__ == "__main__":
    main()
