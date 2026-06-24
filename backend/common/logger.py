"""
日志记录模块

提供统一的日志记录功能，支持不同级别和格式的日志输出。
"""

import logging
import sys
from typing import Optional


class Logger:
    def __init__(self, name: str = "app", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        self.logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)

    def _log(self, level: int, message: str, exc_info: bool = False, **kwargs):
        if exc_info:
            self.logger.log(level, message, exc_info=True)
        else:
            self.logger.log(level, message)


logger = Logger("course-knowledge-system")


def get_logger(name: Optional[str] = None) -> Logger:
    if name:
        return Logger(name)
    return logger
