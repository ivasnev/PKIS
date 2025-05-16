import logging
from typing import Dict

from utils.interfaces import ICommandHandler, IClientInterface

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HelpCommandHandler(ICommandHandler):
    """Обработчик команды помощи"""
    
    def __init__(self, interface: IClientInterface):
        """
        Инициализация обработчика
        
        :param interface: Интерфейс клиента
        """
        self.interface = interface
    
    async def execute(self, args: str) -> bool:
        """
        Выполняет команду справки
        
        :param args: Аргументы команды
        :return: True, если команда выполнена успешно
        """
        commands = self.interface.get_commands()
        
        self.interface.display_message("\n=== Доступные команды ===")
        
        for command_name, handler in commands.items():
            description = getattr(handler, 'description', None) or "Нет описания"
            self.interface.display_message(f"{command_name}: {description}")
            
        self.interface.display_message("\nПримеры использования команд:")
        self.interface.display_message("guess ABCD - отправить догадку ABCD")
        self.interface.display_message("chat Привет всем! - отправить сообщение в чат")
        self.interface.display_message("start - запустить игру, когда набралось достаточно игроков")
        
        return True
    
    @property
    def description(self) -> str:
        """
        Возвращает справку по команде
        
        :return: Текст справки
        """
        return "показать справку по доступным командам"
