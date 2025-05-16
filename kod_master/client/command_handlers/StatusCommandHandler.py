import logging
from typing import Dict, Any, Optional
from utils.interfaces import ICommandHandler, IGameClient, IClientInterface

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StatusCommandHandler(ICommandHandler):
    """Обработчик команды статуса"""

    def __init__(self, client: IGameClient):
        """
        Инициализация обработчика

        :param client: Клиент игры
        """
        self.client = client

    @property
    def description(self) -> str:
        """
        Возвращает справку по команде

        :return: Текст справки
        """
        return "показать текущий статус игры"

    async def execute(self, args: str) -> bool:
        """
        Выполняет команду статуса

        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        logger.info("\n=== Статус игры ===")
        
        if self.client.game_active:
            players_str = ", ".join(self.client.players)
            logger.info(f"Статус: Игра активна")
            logger.info(f"ID игры: {self.client.current_game_id}")
            logger.info(f"Длина кода: {self.client.game_info.get('code_length', 4)}")
            logger.info(f"Доступно попыток: {self.client.game_info.get('allowed_attempts', 10)}")
            logger.info(f"Игроки: {players_str}")
            logger.info(f"Ваш ход: {'Да' if self.client.is_my_turn else 'Нет'}")
        else:
            logger.info("Статус: Ожидание начала игры")
            
            # Отображаем информацию о позиции в очереди
            if self.client.queue_position > 0:
                if self.client.will_play_next:
                    status = "В следующей игре"
                    logger.info(f"Позиция в очереди: {self.client.queue_position} из {self.client.total_in_queue} (✓ {status})")
                else:
                    status = "В ожидании"
                    logger.info(f"Позиция в очереди: {self.client.queue_position} из {self.client.total_in_queue} (⏱ {status})")
                
                # Показываем оценку ожидания
                if not self.client.will_play_next and self.client.total_in_queue > self.client.queue_position:
                    estimated_games = (self.client.queue_position - 1) // 4 + 1
                    logger.info(f"Примерное ожидание: {estimated_games} игр{'а' if 1 < estimated_games < 5 else ''}")
            else:
                logger.info("Вы пока не находитесь в очереди.")
            
            logger.info("Используйте команду 'start' для запуска игры, когда будет достаточно игроков")
        
        return True