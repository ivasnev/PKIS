from typing import Dict, Any
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

class ChatCommandHandler(ICommandHandler):
    """Обработчик команды 'chat'"""

    def __init__(self, client: IGameClient):
        """
        Инициализация обработчика

        :param client: Клиент игры
        """
        self._client = client

    @property
    def description(self) -> str:
        """Возвращает описание команды"""
        return "Отправить сообщение в чат (например, 'chat Привет!')"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        if not args:
            print("Использование: chat <сообщение>")
            return False

        # Отправляем сообщение в чат
        if await self._client.send_chat_message(args):
            return True
        else:
            print("Не удалось отправить сообщение")
            return False