import asyncio
import json
import logging
from typing import Optional, Dict, List, Callable

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameClient:
    """Класс клиента для игры 'Код-Мастер'"""
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        """
        Инициализация клиента
        
        :param host: Хост сервера
        :param port: Порт сервера
        """
        self.host = host
        self.port = port
        
        # Соединение с сервером
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        
        # Идентификатор игрока
        self.player_id: Optional[str] = None
        
        # Идентификатор текущей игры
        self.current_game_id: Optional[str] = None
        
        # Флаг, указывающий, активна ли игра
        self.game_active = False
        
        # Флаг, указывающий, ход ли текущего игрока
        self.is_my_turn = False
        
        # Информация о текущей игре
        self.game_info: Dict = {}
        
        # Список игроков в текущей игре
        self.players: List[str] = []
        
        # Обработчики сообщений
        self.message_handlers: Dict[str, List[Callable]] = {}
        
        # Флаг подключения
        self.connected = False
        
        # Задача получения сообщений
        self.receive_task: Optional[asyncio.Task] = None
    
    async def connect(self) -> bool:
        """
        Подключается к серверу
        
        :return: True, если подключение успешно, False в противном случае
        """
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            self.connected = True
            
            # Запускаем задачу получения сообщений
            self.receive_task = asyncio.create_task(self.receive_messages())
            
            logger.info(f"Подключено к серверу {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при подключении к серверу: {e}")
            return False
    
    async def disconnect(self):
        """Отключается от сервера"""
        if not self.connected:
            return
        
        self.connected = False
        
        # Отменяем задачу получения сообщений
        if self.receive_task:
            self.receive_task.cancel()
            
        # Закрываем соединение
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
        logger.info("Отключено от сервера")
    
    async def send_message(self, message: Dict) -> bool:
        """
        Отправляет сообщение на сервер
        
        :param message: Сообщение для отправки
        :return: True, если отправка успешна, False в противном случае
        """
        if not self.connected or not self.writer:
            return False
        
        try:
            self.writer.write((json.dumps(message) + "\n").encode())
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return False
    
    async def send_guess(self, guess: str) -> bool:
        """
        Отправляет догадку на сервер
        
        :param guess: Догадка игрока
        :return: True, если отправка успешна, False в противном случае
        """
        if not self.connected or not self.game_active or not self.is_my_turn:
            return False
        
        return await self.send_message({
            "type": "guess",
            "guess": guess.upper()
        })
    
    async def send_chat_message(self, text: str) -> bool:
        """
        Отправляет сообщение в чат
        
        :param text: Текст сообщения
        :return: True, если отправка успешна, False в противном случае
        """
        if not self.connected:
            return False
        
        return await self.send_message({
            "type": "chat",
            "text": text
        })
    
    async def receive_messages(self):
        """Получает сообщения от сервера"""
        try:
            while self.connected and self.reader:
                # Читаем данные от сервера
                data = await self.reader.readline()
                if not data:
                    logger.info("Соединение с сервером закрыто")
                    break
                
                # Обрабатываем сообщение
                try:
                    message = json.loads(data.decode().strip())
                    await self.handle_message(message)
                except json.JSONDecodeError:
                    logger.error("Получены некорректные данные от сервера")
        except asyncio.CancelledError:
            logger.info("Получение сообщений отменено")
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений: {e}")
        finally:
            await self.disconnect()
    
    async def handle_message(self, message: Dict):
        """
        Обрабатывает сообщение от сервера
        
        :param message: Полученное сообщение
        """
        message_type = message.get("type", "unknown")
        
        # Обработка приветственного сообщения
        if message_type == "welcome":
            self.player_id = message.get("player_id")
            logger.info(f"Получен ID игрока: {self.player_id}")
        
        # Обработка начала игры
        elif message_type == "game_start":
            self.current_game_id = message.get("game_id")
            self.game_active = True
            self.players = message.get("players", [])
            self.game_info = {
                "code_length": message.get("code_length", 4),
                "allowed_attempts": message.get("allowed_attempts", 10)
            }
            logger.info(f"Игра началась. ID: {self.current_game_id}")
        
        # Обработка окончания игры
        elif message_type == "game_end":
            self.game_active = False
            self.is_my_turn = False
            winner = message.get("winner")
            secret_code = message.get("secret_code")
            
            if winner == self.player_id:
                logger.info(f"Вы выиграли! Секретный код: {secret_code}")
            elif winner:
                logger.info(f"Игрок {winner} выиграл. Секретный код: {secret_code}")
            else:
                logger.info(f"Игра завершена без победителя. Секретный код: {secret_code}")
                
            self.current_game_id = None
        
        # Обработка сообщения о ходе
        elif message_type == "your_turn":
            self.is_my_turn = True
            logger.info("Ваш ход! Введите догадку.")
        
        # Обработка смены хода
        elif message_type == "turn_change":
            next_player = message.get("player_id")
            self.is_my_turn = next_player == self.player_id
            
            if self.is_my_turn:
                logger.info("Ваш ход!")
            else:
                logger.info(f"Ход игрока {next_player}")
        
        # Обработка результата догадки
        elif message_type == "guess_result":
            player_id = message.get("player_id")
            guess = message.get("guess")
            black_markers = message.get("black_markers", 0)
            white_markers = message.get("white_markers", 0)
            attempts = message.get("attempts", 0)
            
            if player_id == self.player_id:
                logger.info(f"Ваша догадка: {guess}")
            else:
                logger.info(f"Догадка игрока {player_id}: {guess}")
                
            logger.info(f"Черные маркеры: {black_markers}, Белые маркеры: {white_markers}")
        
        # Обработка сообщений чата
        elif message_type == "chat":
            player_id = message.get("player_id")
            text = message.get("text")
            
            if player_id == self.player_id:
                logger.info(f"Вы: {text}")
            else:
                logger.info(f"Игрок {player_id}: {text}")
        
        # Обработка ошибок
        elif message_type == "error":
            error_message = message.get("message")
            logger.error(f"Ошибка: {error_message}")
        
        # Вызов пользовательских обработчиков
        handlers = self.message_handlers.get(message_type, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Ошибка в обработчике {handler.__name__}: {e}")
    
    def add_message_handler(self, message_type: str, handler: Callable):
        """
        Добавляет обработчик сообщений определенного типа
        
        :param message_type: Тип сообщения
        :param handler: Функция-обработчик
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
            
        self.message_handlers[message_type].append(handler)
    
    def remove_message_handler(self, message_type: str, handler: Callable) -> bool:
        """
        Удаляет обработчик сообщений
        
        :param message_type: Тип сообщения
        :param handler: Функция-обработчик
        :return: True, если обработчик удален, False в противном случае
        """
        if message_type not in self.message_handlers:
            return False
            
        try:
            self.message_handlers[message_type].remove(handler)
            return True
        except ValueError:
            return False
