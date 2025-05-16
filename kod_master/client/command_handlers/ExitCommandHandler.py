from typing import Dict, Any
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

class ExitCommandHandler(ICommandHandler):
    """Обработчик команды 'exit'"""

    def __init__(self, interface: IClientInterface):
        """
        Инициализация обработчика

        :param interface: Интерфейс клиента
        """
        self._interface = interface

    @property
    def description(self) -> str:
        """Возвращает описание команды"""
        return "Выйти из игры"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        print("\nВыход из игры...")
        await self._interface.stop()
        return True