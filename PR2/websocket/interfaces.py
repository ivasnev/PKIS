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


class AnalysisInterface(ABC):
    """Интерфейс для анализа файлов"""

    @abstractmethod
    async def analyze_file(self, filename: str, content: str) -> Any:
        """Анализирует содержимое файла"""
        pass

    @abstractmethod
    async def analyze_files(self, files: list) -> list:
        """Анализирует несколько файлов"""
        pass


class WebSocketHandlerInterface(ABC):
    """Интерфейс для обработки WebSocket соединений"""

    @abstractmethod
    async def handle_client(self, websocket, path) -> None:
        """Обрабатывает клиентские соединения"""
        pass

    @abstractmethod
    async def send_error(self, websocket, message: str) -> None:
        """Отправляет сообщение об ошибке клиенту"""
        pass
