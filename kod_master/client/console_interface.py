import asyncio
import signal
import logging
import sys
from typing import Dict, Optional, List, Type

from utils.interfaces import IClientInterface, IGameClient, ICommandHandler, IMessageHandler
from client.client import GameClient
from client.command_handlers import HelpCommandHandler, GuessCommandHandler, ChatCommandHandler, StatusCommandHandler, ExitCommandHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsoleInterface(IClientInterface):
    """Консольный интерфейс для игры"""
    
    def __init__(self, client: IGameClient, command_handlers: Optional[Dict[str, ICommandHandler]] = None):
        """
        Инициализация консольного интерфейса
        
        :param client: Клиент игры
        :param command_handlers: Словарь обработчиков команд
        """
        self.client = client
        self.running = False
        self.input_task = None
        
        # Инициализация обработчиков команд
        if command_handlers:
            self.commands = command_handlers
        else:
            # Создаем стандартные обработчики команд
            self.commands = {}
            self._register_default_commands()
            
    def _register_default_commands(self):
        """Регистрирует стандартные обработчики команд"""
        default_handlers = [
            HelpCommandHandler(self),
            GuessCommandHandler(self.client),
            ChatCommandHandler(self.client),
            StatusCommandHandler(self.client),
            ExitCommandHandler(self)
        ]
        
        for handler in default_handlers:
            command_name = handler.__class__.__name__.lower().replace('commandhandler', '')
            self.commands[command_name] = handler
    
    def register_command(self, command: str, handler: ICommandHandler):
        """
        Регистрирует обработчик команды
        
        :param command: Название команды
        :param handler: Обработчик команды
        """
        self.commands[command.lower()] = handler
    
    def register_message_handler(self, message_type: str, handler: IMessageHandler):
        """
        Регистрирует обработчик сообщений от сервера
        
        :param message_type: Тип сообщения
        :param handler: Обработчик сообщения
        """
        self.client.add_message_handler(message_type, handler)
        
    async def start(self):
        """Запускает интерфейс"""
        # Подключаемся к серверу
        if not await self.client.connect():
            logger.error("Не удалось подключиться к серверу")
            return
        
        self.running = True
        
        # Устанавливаем обработчики сигналов
        self._setup_signal_handlers()
        
        # Запускаем цикл чтения команд
        self.input_task = asyncio.create_task(self._input_loop())
        
        try:
            # Ждем завершения чтения команд
            await self.input_task
        except asyncio.CancelledError:
            logger.info("Ввод команд отменен")
        finally:
            # Отключаем клиент при выходе
            await self.stop()
    
    async def stop(self):
        """Останавливает интерфейс"""
        self.running = False
        
        if self.input_task:
            self.input_task.cancel()
            
        await self.client.disconnect()
    
    def _setup_signal_handlers(self):
        """Устанавливает обработчики сигналов"""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
    
    async def _input_loop(self):
        """Цикл чтения и обработки команд из командной строки"""
        self.display_message("\n=== Игра \"Код-Мастер\" ===")
        self.display_message("Используйте команду 'help' для просмотра доступных команд")
        
        while self.running:
            try:
                # Ждем ввод пользователя
                user_input = await asyncio.to_thread(input, "\n> ")
                
                # Обрабатываем ввод
                await self.handle_input(user_input)
                
            except EOFError:
                # Обработка Ctrl+D
                await self.stop()
            except KeyboardInterrupt:
                # Обработка Ctrl+C
                await self.stop()
            except Exception as e:
                logger.error(f"Ошибка при обработке ввода: {e}")
    
    def display_message(self, message: str):
        """
        Отображает сообщение
        
        :param message: Текст сообщения
        """
        print(message)
    
    async def handle_input(self, input_data: str):
        """
        Обрабатывает ввод пользователя
        
        :param input_data: Строка ввода пользователя
        """
        # Игнорируем пустые строки
        if not input_data.strip():
            return
        
        # Разбираем ввод на команду и аргументы
        parts = input_data.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Вызываем обработчик команды
        if command in self.commands:
            await self.commands[command].execute(args)
        else:
            self.display_message(f"Неизвестная команда: {command}")
            self.display_message("Используйте 'help' для получения списка команд")
    
    def get_commands(self) -> Dict[str, ICommandHandler]:
        """
        Возвращает словарь доступных команд
        
        :return: Словарь команд
        """
        return self.commands


class ConsoleClientInterface:
    """Фасад для консольного интерфейса, обеспечивающий обратную совместимость"""
    
    def __init__(self, host: str, port: int):
        """
        Инициализация интерфейса командной строки
        
        :param host: Хост сервера
        :param port: Порт сервера
        """
        self.client = GameClient(host=host, port=port)
        self.interface = ConsoleInterface(self.client)
        self.running = False
    
    async def start(self):
        """Запускает клиент и интерфейс командной строки"""
        await self.interface.start()
    
    async def command_exit(self, args: str):
        """
        Выходит из игры (для обратной совместимости)
        
        :param args: Аргументы команды
        """
        await self.interface.stop() 