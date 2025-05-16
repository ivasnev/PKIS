import logging
from typing import Optional

from utils.interfaces import ICommandHandler, IGameClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StartCommandHandler(ICommandHandler):
    """Обработчик команды запуска игры"""
    
    def __init__(self, client: IGameClient):
        """
        Инициализация обработчика
        
        :param client: Клиент игры
        """
        self.client = client
    
    async def execute(self, args: str) -> bool:
        """
        Выполняет команду запуска игры
        
        :param args: Аргументы команды
        :return: True, если команда выполнена успешно, False в противном случае
        """
        # Отправляем запрос на запуск игры
        result = await self.client.send_message({
            "type": "start_game"
        })
        
        if result:
            logger.info("Отправлен запрос на запуск игры")
            return True
        else:
            logger.error("Не удалось отправить запрос на запуск игры")
            return False

    @property
    def description(self) -> str:
        """
        Возвращает справку по команде
        
        :return: Текст справки
        """
        return "start - запросить начало игры, если есть достаточное количество игроков" 