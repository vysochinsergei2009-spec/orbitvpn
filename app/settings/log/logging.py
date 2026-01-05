import logging
from app.settings.config import env


def get_logger(name: str):
    logger = logging.getLogger(name)

    if not env.IS_LOGGING:
        logger.disabled = True
        return logger

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, env.LOG_LEVEL.upper(), logging.INFO))

    return logger


def setup_aiogram_logger():
    aiolog = logging.getLogger("aiogram")

    if not env.LOG_AIOGRAM:
        aiolog.disabled = True
        return

    aiolog.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] AIROUTER %(levelname)s: %(message)s"
    )
    handler.setFormatter(formatter)

    aiolog.addHandler(handler)
    aiolog.setLevel(getattr(logging, env.LOG_LEVEL.upper(), logging.INFO))