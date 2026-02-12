# app/logger.py
import logging
import sys
import json_log_formatter

def get_logger(name: str = "telegram_bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger   # already configured

    logger.setLevel(logging.getLevelName(__import__("app.config").settings.LOG_LEVEL))

    formatter = json_log_formatter.JSONFormatter(
        keys=["level", "timestamp", "name", "message", "pathname", "lineno"]
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
