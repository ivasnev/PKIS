from typing import Dict, Any
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

class GuessCommandHandler(ICommandHandler):
    """Обработчик команды 'guess'"""

    def __init__(self, client: IGameClient):
        """
        Инициализация обработчика

        :param client: Клиент игры
        """
        self._client = client

    @property
    def description(self) -> str:
        """Возвращает описание команды"""
        return "Отправить догадку (например, 'guess ABCD')"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        if not args:
            print("Использование: guess <код>")
            return False

        guess = args.strip()

        if not self._client.game_active:
            print("Игра не активна")
            return False

        if not self._client.is_my_turn:
            print("Сейчас не ваш ход")
            return False

        # Отправляем догадку на сервер
        if await self._client.send_guess(guess):
            print(f"Догадка отправлена: {guess}")
            return True
        else:
            print("Не удалось отправить догадку")
            return False