import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional

from utils.game_logic import GameLogic
from utils.xml_handler import XMLHandler
from utils.interfaces import IGameServer, IGameLogic, IXMLHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameServer(IGameServer):
    """Класс сервера для игры 'Код-Мастер'"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8888,
                 min_players: int = 2, max_players: int = 4,
                 code_length: int = 4, allowed_attempts: int = 10,
                 game_logic: Optional[IGameLogic] = None,
                 xml_handler: Optional[IXMLHandler] = None):
        """
        Инициализация сервера
        
        :param host: Хост для прослушивания
        :param port: Порт для прослушивания
        :param min_players: Минимальное количество игроков
        :param max_players: Максимальное количество игроков
        :param code_length: Длина секретного кода
        :param allowed_attempts: Максимальное количество попыток
        :param game_logic: Объект игровой логики
        :param xml_handler: Объект обработчика XML
        """
        self.host = host
        self.port = port
        self.min_players = min_players
        self.max_players = max_players
        self.code_length = code_length
        self.allowed_attempts = allowed_attempts
        
        # Словарь для хранения соединений игроков
        self.players: Dict[str, asyncio.StreamWriter] = {}
        
        # Набор игроков, ожидающих начала игры
        self.waiting_players: Set[str] = set()
        
        # Набор игроков в текущей игре
        self.active_players: Set[str] = set()
        
        # Очередь игроков для хода
        self.player_queue: List[str] = []
        self.current_player_index = 0
        
        # Объект игровой логики
        self.game_logic = game_logic or GameLogic(
            code_length=code_length,
            allowed_attempts=allowed_attempts,
            min_players=min_players,
            max_players=max_players
        )
        
        # Обработчик XML
        self.xml_handler = xml_handler or XMLHandler()
        
        # Идентификатор текущей игры
        self.current_game_id: Optional[str] = None
        
        # Время начала текущей игры
        self.game_start_time: Optional[datetime] = None
        
        # Флаг работы сервера
        self.running = False
    
    async def start(self):
        """Запускает сервер"""
        self.running = True
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"Сервер запущен на {self.host}:{self.port}")
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Обрабатывает подключение нового клиента
        
        :param reader: Объект для чтения данных от клиента
        :param writer: Объект для отправки данных клиенту
        """
        # Генерируем уникальный идентификатор для игрока
        player_id = str(uuid.uuid4())
        
        # Сохраняем соединение
        self.players[player_id] = writer
        self.waiting_players.add(player_id)
        
        # Отправляем приветственное сообщение
        await self.send_message(player_id, {
            "type": "welcome",
            "player_id": player_id,
            "message": f"Добро пожаловать в игру 'Код-Мастер'! Ваш ID: {player_id}"
        })
        
        logger.info(f"Новый игрок подключился: {player_id}")
        
        # Проверяем, можно ли начать игру
        await self.check_start_game()
        
        try:
            while self.running:
                # Читаем данные от клиента
                data = await reader.readline()
                if not data:
                    break
                
                # Обрабатываем сообщение
                await self.process_message(player_id, data)
        except asyncio.CancelledError:
            logger.info(f"Соединение с игроком {player_id} отменено")
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения от игрока {player_id}: {e}")
        finally:
            # Удаляем игрока при отключении
            await self.remove_player(player_id)
            writer.close()
            await writer.wait_closed()
    
    async def remove_player(self, player_id: str):
        """
        Удаляет игрока при отключении
        
        :param player_id: Идентификатор игрока
        """
        logger.info(f"Игрок {player_id} отключился")
        
        # Удаляем игрока из всех списков
        if player_id in self.players:
            del self.players[player_id]
        
        self.waiting_players.discard(player_id)
        self.active_players.discard(player_id)
        
        if player_id in self.player_queue:
            self.player_queue.remove(player_id)
        
        # Если игра активна и отключился активный игрок, завершаем игру
        if self.current_game_id and len(self.active_players) < self.min_players:
            await self.end_game(None)
            
            # Пытаемся начать новую игру с оставшимися игроками
            await self.check_start_game()
    
    async def process_message(self, player_id: str, data: bytes):
        """
        Обрабатывает сообщение от клиента
        
        :param player_id: Идентификатор игрока
        :param data: Данные от клиента
        """
        try:
            message = json.loads(data.decode().strip())
            message_type = message.get("type", "unknown")
            
            if message_type == "guess":
                # Проверяем, что игра активна и это ход данного игрока
                if (self.current_game_id and 
                    player_id in self.active_players and 
                    player_id == self.player_queue[self.current_player_index]):
                    
                    guess = message.get("guess", "").upper()
                    await self.process_guess(player_id, guess)
                else:
                    await self.send_message(player_id, {
                        "type": "error",
                        "message": "Сейчас не ваш ход или игра не активна"
                    })
            
            elif message_type == "chat":
                # Обрабатываем сообщение чата
                text = message.get("text", "")
                await self.broadcast_message({
                    "type": "chat",
                    "player_id": player_id,
                    "text": text
                }, exclude=[])
                
        except json.JSONDecodeError:
            logger.error(f"Получены некорректные данные от игрока {player_id}")
            await self.send_message(player_id, {
                "type": "error",
                "message": "Некорректный формат сообщения"
            })
    
    async def process_guess(self, player_id: str, guess: str):
        """
        Обрабатывает попытку угадать код
        
        :param player_id: Идентификатор игрока
        :param guess: Догадка игрока
        """
        # Проверяем, что длина догадки соответствует длине кода
        if len(guess) != self.code_length:
            await self.send_message(player_id, {
                "type": "error",
                "message": f"Длина кода должна быть {self.code_length} символов"
            })
            return
        
        # Получаем результат проверки
        result = self.game_logic.make_guess(player_id, guess)
        
        # Если игрок выиграл или игра завершена
        if result.get("game_over", False):
            await self.broadcast_message({
                "type": "guess_result",
                "player_id": player_id,
                "guess": guess,
                "black_markers": result.get("black_markers", 0),
                "white_markers": result.get("white_markers", 0),
                "attempts": result.get("attempts", 0)
            }, exclude=[])
            
            # Завершаем игру
            await self.end_game(result.get("is_winner", False) and player_id or None)
        else:
            # Отправляем результат проверки
            await self.broadcast_message({
                "type": "guess_result",
                "player_id": player_id,
                "guess": guess,
                "black_markers": result.get("black_markers", 0),
                "white_markers": result.get("white_markers", 0),
                "attempts": result.get("attempts", 0)
            }, exclude=[])
            
            # Переходим к следующему игроку
            self.current_player_index = (self.current_player_index + 1) % len(self.player_queue)
            next_player = self.player_queue[self.current_player_index]
            
            # Оповещаем всех о смене хода
            await self.broadcast_message({
                "type": "turn_change",
                "player_id": next_player
            }, exclude=[])
            
            # Напоминаем текущему игроку, что его ход
            await self.send_message(next_player, {
                "type": "your_turn",
                "message": "Ваш ход! Введите догадку."
            })
    
    async def check_start_game(self):
        """Проверяет, можно ли начать новую игру"""
        # Если нет активной игры и достаточно ожидающих игроков
        if (not self.current_game_id and 
            self.min_players <= len(self.waiting_players) <= self.max_players):
            
            # Начинаем игру
            await self.start_game()
    
    async def start_game(self):
        """Начинает новую игру"""
        # Создаем идентификатор игры
        self.current_game_id = str(uuid.uuid4())
        self.game_start_time = datetime.now()
        
        # Переносим игроков из ожидающих в активные
        self.active_players = set(list(self.waiting_players)[:self.max_players])
        self.waiting_players -= self.active_players
        
        # Формируем очередь игроков
        self.player_queue = list(self.active_players)
        self.current_player_index = 0
        
        # Инициализируем игровую логику
        if not self.game_logic.start_new_game(list(self.active_players)):
            logger.error(f"Не удалось начать игру. ID: {self.current_game_id}")
            return
        
        logger.info(f"Начата новая игра. ID: {self.current_game_id}, "
                   f"Код: {self.game_logic.secret_code}, "
                   f"Игроки: {self.active_players}")
        
        # Оповещаем всех игроков о начале игры
        await self.broadcast_message({
            "type": "game_start",
            "game_id": self.current_game_id,
            "players": list(self.active_players),
            "code_length": self.code_length,
            "allowed_attempts": self.allowed_attempts
        }, exclude=[])
        
        # Оповещаем первого игрока о его ходе
        first_player = self.player_queue[0]
        await self.send_message(first_player, {
            "type": "your_turn",
            "message": "Ваш ход! Введите догадку."
        })
    
    async def end_game(self, winner: Optional[str]):
        """
        Завершает текущую игру
        
        :param winner: Идентификатор победителя (None, если никто не выиграл)
        """
        if not self.current_game_id:
            return
        
        end_time = datetime.now()
        
        # Получаем информацию о игре
        game_status = self.game_logic.get_game_status()
        secret_code = game_status.get("code", "UNKNOWN")
        player_attempts = game_status.get("player_attempts", {})
        
        # Сохраняем результаты в XML
        file_path = self.xml_handler.save_game_result(
            game_id=self.current_game_id,
            start_time=self.game_start_time,
            end_time=end_time,
            secret_code=secret_code,
            player_attempts=player_attempts,
            winner=winner
        )
        
        logger.info(f"Игра {self.current_game_id} завершена. "
                   f"Победитель: {winner or 'Нет победителя'}. "
                   f"Результаты сохранены в {file_path}")
        
        # Отправляем всем игрокам сообщение о завершении игры
        await self.broadcast_message({
            "type": "game_end",
            "winner": winner,
            "secret_code": secret_code,
            "player_attempts": player_attempts
        }, exclude=[])
        
        # Сбрасываем состояние
        self.current_game_id = None
        self.game_start_time = None
        self.active_players = set()
        self.player_queue.clear()
        self.current_player_index = 0
        
        # Пробуем начать новую игру
        await self.check_start_game()
    
    async def send_message(self, player_id: str, message: Dict):
        """
        Отправляет сообщение указанному игроку
        
        :param player_id: Идентификатор игрока
        :param message: Сообщение для отправки
        """
        if player_id not in self.players:
            return
        
        writer = self.players[player_id]
        try:
            writer.write((json.dumps(message) + "\n").encode())
            await writer.drain()
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения игроку {player_id}: {e}")
            # Удаляем игрока при ошибке отправки
            await self.remove_player(player_id)
    
    async def broadcast_message(self, message: Dict, exclude: List[str]):
        """
        Отправляет сообщение всем активным игрокам
        
        :param message: Сообщение для отправки
        :param exclude: Список игроков, которым не отправлять сообщение
        """
        for player_id in self.players:
            if player_id not in exclude:
                await self.send_message(player_id, message)
