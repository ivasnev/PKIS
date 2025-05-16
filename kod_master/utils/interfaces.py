"""Модуль интерфейсов для игры Код-Мастер"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
import asyncio


class IGameLogic(ABC):
    """Интерфейс игровой логики"""
    
    @abstractmethod
    def generate_secret_code(self) -> str:
        """Генерирует случайный секретный код"""
        pass
    
    @abstractmethod
    def start_new_game(self, player_ids: List[str]) -> bool:
        """Начинает новую игру"""
        pass
    
    @abstractmethod
    def check_guess(self, guess: str) -> Tuple[int, int]:
        """Проверяет догадку и возвращает количество черных и белых маркеров"""
        pass
    
    @abstractmethod
    def make_guess(self, player_id: str, guess: str) -> Dict:
        """Обрабатывает попытку игрока угадать код"""
        pass
    
    @abstractmethod
    def get_game_status(self) -> Dict:
        """Возвращает текущий статус игры"""
        pass


class IXMLHandler(ABC):
    """Интерфейс обработчика XML"""
    
    @abstractmethod
    def save_game_result(self, game_id: str, start_time: datetime, end_time: datetime, 
                         secret_code: str, player_attempts: Dict[str, int], 
                         winner: Optional[str] = None) -> str:
        """Сохраняет результаты игры в XML-файл"""
        pass
    
    @abstractmethod
    def load_game_results(self, limit: int = 10) -> List[Dict]:
        """Загружает последние результаты игр"""
        pass


class IGameServer(ABC):
    """Интерфейс сервера игры"""
    
    @abstractmethod
    async def start(self):
        """Запускает сервер"""
        pass
    
    @abstractmethod
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Обрабатывает подключение нового клиента"""
        pass
    
    @abstractmethod
    async def send_message(self, player_id: str, message: Dict):
        """Отправляет сообщение указанному игроку"""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: Dict, exclude: List[str]):
        """Отправляет сообщение всем активным игрокам"""
        pass


class IGameClient(ABC):
    """Интерфейс клиента игры"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Подключается к серверу"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Отключается от сервера"""
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict) -> bool:
        """Отправляет сообщение на сервер"""
        pass
    
    @abstractmethod
    async def send_guess(self, guess: str) -> bool:
        """Отправляет догадку на сервер"""
        pass
    
    @abstractmethod
    async def handle_message(self, message: Dict):
        """Обрабатывает сообщение от сервера"""
        pass


class IClientInterface(ABC):
    """Интерфейс пользовательского интерфейса клиента"""
    
    @abstractmethod
    async def start(self):
        """Запускает интерфейс"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Останавливает интерфейс"""
        pass
    
    @abstractmethod
    def display_message(self, message: str):
        """Отображает сообщение"""
        pass
    
    @abstractmethod
    async def handle_input(self, input_data: str):
        """Обрабатывает ввод пользователя"""
        pass


class ICommandHandler(ABC):
    """Интерфейс обработчика команд"""
    
    @abstractmethod
    async def execute(self, args: str) -> bool:
        """Выполняет команду"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Возвращает описание команды"""
        pass


class IMessageHandler(ABC):
    """Интерфейс обработчика сообщений"""
    
    @abstractmethod
    async def handle(self, message: Dict) -> bool:
        """Обрабатывает сообщение"""
        pass 