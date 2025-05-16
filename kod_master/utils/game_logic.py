import random
import string
from typing import Tuple, List, Dict

from utils.interfaces import IGameLogic


class GameLogic(IGameLogic):
    """Класс, отвечающий за логику игры 'Код-Мастер'"""
    
    def __init__(self, code_length: int = 4, allowed_attempts: int = 10, 
                 use_letters: bool = True, use_numbers: bool = True,
                 min_players: int = 2, max_players: int = 4):
        """
        Инициализация игровой логики
        
        :param code_length: Длина кода
        :param allowed_attempts: Максимальное количество попыток
        :param use_letters: Использовать буквы в коде
        :param use_numbers: Использовать цифры в коде
        :param min_players: Минимальное количество игроков
        :param max_players: Максимальное количество игроков
        """
        self.code_length = code_length
        self.allowed_attempts = allowed_attempts
        self.use_letters = use_letters
        self.use_numbers = use_numbers
        self.min_players = min_players
        self.max_players = max_players
        
        self.secret_code = None
        self.current_turn = 0
        self.player_attempts = {}  # Словарь для хранения количества попыток каждого игрока
        self.winner = None
        self.game_over = False
        
    def generate_secret_code(self) -> str:
        """Генерирует случайный секретный код"""
        characters = ""
        if self.use_letters:
            characters += string.ascii_uppercase
        if self.use_numbers:
            characters += string.digits
            
        if not characters:
            characters = string.ascii_uppercase + string.digits
            
        return ''.join(random.choice(characters) for _ in range(self.code_length))
    
    def start_new_game(self, player_ids: List[str]) -> bool:
        """
        Начинает новую игру
        
        :param player_ids: Список идентификаторов игроков
        :return: True, если игра успешно начата, False в противном случае
        """
        if not self.min_players <= len(player_ids) <= self.max_players:
            return False
        
        self.secret_code = self.generate_secret_code()
        self.current_turn = 0
        self.player_attempts = {player_id: 0 for player_id in player_ids}
        self.winner = None
        self.game_over = False
        
        return True
    
    def check_guess(self, guess: str) -> Tuple[int, int]:
        """
        Проверяет догадку пользователя и возвращает количество черных и белых маркеров
        
        :param guess: Догадка пользователя
        :return: Кортеж из количества черных и белых маркеров
        """
        if len(guess) != self.code_length:
            return 0, 0
        
        # Преобразуем все символы в верхний регистр
        guess = guess.upper()
        
        # Черные маркеры (правильный символ на правильной позиции)
        black_markers = sum(1 for i in range(self.code_length) if guess[i] == self.secret_code[i])
        
        # Для подсчета белых маркеров нужно учесть символы, которые уже посчитаны как черные
        secret_code_copy = list(self.secret_code)
        guess_copy = list(guess)
        
        # Удаляем символы, учтённые для черных маркеров
        for i in range(self.code_length - 1, -1, -1):
            if guess[i] == self.secret_code[i]:
                secret_code_copy.pop(i)
                guess_copy.pop(i)
        
        # Белые маркеры (правильный символ на неправильной позиции)
        white_markers = 0
        for char in guess_copy[:]:
            if char in secret_code_copy:
                white_markers += 1
                secret_code_copy.remove(char)
                
        return black_markers, white_markers
    
    def make_guess(self, player_id: str, guess: str) -> Dict:
        """
        Обрабатывает попытку игрока угадать код
        
        :param player_id: Идентификатор игрока
        :param guess: Догадка игрока
        :return: Словарь с результатами попытки
        """
        if self.game_over or player_id not in self.player_attempts:
            return {
                "error": "Игра не активна или игрок не участвует",
                "game_over": self.game_over
            }
        
        # Увеличиваем счетчик попыток игрока
        self.player_attempts[player_id] += 1
        
        # Проверяем догадку
        black_markers, white_markers = self.check_guess(guess)
        
        # Проверяем, выиграл ли игрок
        if black_markers == self.code_length:
            self.winner = player_id
            self.game_over = True
            
        # Проверяем, достигнут ли лимит попыток для всех игроков
        if all(attempts >= self.allowed_attempts for attempts in self.player_attempts.values()):
            self.game_over = True
        
        return {
            "black_markers": black_markers,
            "white_markers": white_markers,
            "is_winner": self.winner == player_id,
            "game_over": self.game_over,
            "attempts": self.player_attempts[player_id]
        }
    
    def get_game_status(self) -> Dict:
        """
        Возвращает текущий статус игры
        
        :return: Словарь с информацией о текущем состоянии игры
        """
        return {
            "game_over": self.game_over,
            "winner": self.winner,
            "code": self.secret_code if self.game_over else None,
            "player_attempts": self.player_attempts
        }
