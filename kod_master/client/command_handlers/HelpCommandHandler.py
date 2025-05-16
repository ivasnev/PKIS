from typing import Dict, Any
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

class HelpCommandHandler(ICommandHandler):
    """Обработчик команды 'help'"""

    def __init__(self, interface: IClientInterface):
        """
        Инициализация обработчика

        :param interface: Интерфейс клиента
        """
        self._interface = interface

    @property
    def description(self) -> str:
        """Возвращает описание команды"""
        return "Показать справку по командам"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        commands = self._interface.get_commands()

        self._interface.display_message("\nДоступные команды:")
        for cmd, handler in commands.items():
            self._interface.display_message(f"  {cmd:<10} - {handler.description}")

        return True
