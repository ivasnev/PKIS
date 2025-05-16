from typing import Dict, Any
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

class StatusCommandHandler(ICommandHandler):
    """Обработчик команды 'status'"""

    def __init__(self, client: IGameClient):
        """
        Инициализация обработчика

        :param client: Клиент игры
        """
        self._client = client

    @property
    def description(self) -> str:
        """Возвращает описание команды"""
        return "Показать текущий статус игры"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        print("\nСтатус игры:")
        print(f"Подключение к серверу: {'Активно' if self._client.connected else 'Не активно'}")
        print(f"ID игрока: {self._client.player_id}")

        if self._client.game_active:
            print(f"Игра активна, ID: {self._client.current_game_id}")
            print(f"Длина кода: {self._client.game_info.get('code_length', 4)}")
            print(f"Максимальное количество попыток: {self._client.game_info.get('allowed_attempts', 10)}")
            print(f"Ваш ход: {'Да' if self._client.is_my_turn else 'Нет'}")
            print(f"Игроки в игре: {', '.join(self._client.players)}")
        else:
            print("Игра не активна")

        return True