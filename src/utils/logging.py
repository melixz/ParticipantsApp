import logging
from rich.console import Console
from rich.logging import RichHandler
from .singleton import SingletonMeta


class AppLogger(metaclass=SingletonMeta):
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger("participant_app")
        self._logger.setLevel(logging.INFO)

        # Настройка rich-форматирования для логов
        console_handler = RichHandler(console=Console())
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def get_logger(self):
        return self._logger
