from abc import ABC, abstractmethod
from typing import Any


class ServerInterface(ABC):
    """Абстрактный класс для серверов"""
    
    @abstractmethod
    async def start(self) -> None:
        """Запускает сервер"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Останавливает сервер"""
        pass


class WebServerHandlerInterface(ABC):
    """Интерфейс для HTTP обработчика"""

    @abstractmethod
    def do_GET(self) -> None:
        """Обрабатывает GET запросы"""
        pass

    @abstractmethod
    def do_POST(self) -> None:
        """Обрабатывает POST запросы"""
        pass
