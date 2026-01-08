import logging
import sys
from pathlib import Path
from typing import Optional

LOG_FILE = Path(__file__).parent / "bot.log"


class ColoredFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    is_logging: bool = True,
    log_to_file: bool = True
) -> None:
    """
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        is_logging: Включить/выключить логирование
        log_to_file: Сохранять логи в файл
    """
    if not is_logging:
        logging.disable(logging.CRITICAL)
        return
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    root_logger.handlers.clear()
    
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    if log_to_file:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(
            LOG_FILE,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def setup_aiogram_logger(log_level: Optional[str] = None) -> None:
    """
    Args:
        log_level: Уровень логирования для aiogram (если None, используется INFO)
    """
    level = getattr(logging, log_level.upper(), logging.INFO) if log_level else logging.INFO
    
    aiogram_loggers = [
        'aiogram',
        'aiogram.dispatcher',
        'aiogram.event',
        'aiogram.bot.api',
    ]
    
    for logger_name in aiogram_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)


def configure_logging_from_env(env_config) -> None:
    is_logging = getattr(env_config, 'IS_LOGGING', True)
    log_level = getattr(env_config, 'LOG_LEVEL', 'INFO')
    log_aiogram = getattr(env_config, 'LOG_AIOGRAM', False)
    
    setup_logging(
        log_level=log_level,
        is_logging=is_logging,
        log_to_file=True
    )
    
    if log_aiogram and is_logging:
        setup_aiogram_logger(log_level)
    else:
        setup_aiogram_logger('WARNING')

try:
    from app.settings.config import env
    configure_logging_from_env(env)
except ImportError:
    setup_logging(log_level="INFO", is_logging=True, log_to_file=True)