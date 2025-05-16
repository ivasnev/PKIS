#!/usr/bin/env python3
import asyncio
import argparse
import logging
import sys
import signal
from client.client import GameClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsoleClientInterface:
    """Класс интерфейса командной строки для клиента игры"""
    
    def __init__(self, host: str, port: int):
        """
        Инициализация интерфейса командной строки
        
        :param host: Хост сервера
        :param port: Порт сервера
        """
        self.client = GameClient(host=host, port=port)
        self.running = False
        self.commands = {
            "help": (self.command_help, "Показать справку по командам"),
            "guess": (self.command_guess, "Отправить догадку"),
            "chat": (self.command_chat, "Отправить сообщение в чат"),
            "status": (self.command_status, "Показать текущий статус игры"),
            "exit": (self.command_exit, "Выйти из игры")
        }
    
    async def start(self):
        """Запускает клиент и интерфейс командной строки"""
        # Подключаемся к серверу
        if not await self.client.connect():
            logger.error("Не удалось подключиться к серверу")
            return
        
        self.running = True
        
        # Устанавливаем обработчик сигнала SIGINT (Ctrl+C)
        self._setup_signal_handlers()
        
        # Запускаем цикл чтения команд
        input_task = asyncio.create_task(self._input_loop())
        
        try:
            # Ждем завершения чтения команд
            await input_task
        except asyncio.CancelledError:
            logger.info("Ввод команд отменен")
        finally:
            # Отключаем клиент при выходе
            await self.client.disconnect()
    
    def _setup_signal_handlers(self):
        """Устанавливает обработчики сигналов"""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.command_exit("")))
    
    async def _input_loop(self):
        """Цикл чтения и обработки команд из командной строки"""
        print("\n=== Игра \"Код-Мастер\" ===")
        print("Используйте команду 'help' для просмотра доступных команд")
        
        while self.running:
            try:
                # Ждем ввод пользователя
                user_input = await asyncio.to_thread(input, "\n> ")
                
                # Игнорируем пустые строки
                if not user_input.strip():
                    continue
                
                # Разбираем ввод на команду и аргументы
                parts = user_input.strip().split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Вызываем обработчик команды
                if command in self.commands:
                    command_handler, _ = self.commands[command]
                    await command_handler(args)
                else:
                    print(f"Неизвестная команда: {command}")
                    print("Используйте 'help' для получения списка команд")
            except EOFError:
                # Обработка Ctrl+D
                await self.command_exit("")
            except KeyboardInterrupt:
                # Обработка Ctrl+C
                await self.command_exit("")
            except Exception as e:
                logger.error(f"Ошибка при обработке ввода: {e}")
    
    async def command_help(self, args: str):
        """
        Показывает справку по командам
        
        :param args: Аргументы команды
        """
        print("\nДоступные команды:")
        for cmd, (_, description) in self.commands.items():
            print(f"  {cmd:<10} - {description}")
    
    async def command_guess(self, args: str):
        """
        Отправляет догадку на сервер
        
        :param args: Аргументы команды (текст догадки)
        """
        if not args:
            print("Использование: guess <код>")
            return
            
        guess = args.strip()
        
        if not self.client.game_active:
            print("Игра не активна")
            return
            
        if not self.client.is_my_turn:
            print("Сейчас не ваш ход")
            return
        
        # Отправляем догадку на сервер
        if await self.client.send_guess(guess):
            print(f"Догадка отправлена: {guess}")
        else:
            print("Не удалось отправить догадку")
    
    async def command_chat(self, args: str):
        """
        Отправляет сообщение в чат
        
        :param args: Аргументы команды (текст сообщения)
        """
        if not args:
            print("Использование: chat <сообщение>")
            return
            
        # Отправляем сообщение в чат
        if await self.client.send_chat_message(args):
            pass
        else:
            print("Не удалось отправить сообщение")
    
    async def command_status(self, args: str):
        """
        Показывает текущий статус игры
        
        :param args: Аргументы команды
        """
        print("\nСтатус игры:")
        print(f"Подключение к серверу: {'Активно' if self.client.connected else 'Не активно'}")
        print(f"ID игрока: {self.client.player_id}")
        
        if self.client.game_active:
            print(f"Игра активна, ID: {self.client.current_game_id}")
            print(f"Длина кода: {self.client.game_info.get('code_length', 4)}")
            print(f"Максимальное количество попыток: {self.client.game_info.get('allowed_attempts', 10)}")
            print(f"Ваш ход: {'Да' if self.client.is_my_turn else 'Нет'}")
            print(f"Игроки в игре: {', '.join(self.client.players)}")
        else:
            print("Игра не активна")
    
    async def command_exit(self, args: str):
        """
        Выходит из игры
        
        :param args: Аргументы команды
        """
        print("\nВыход из игры...")
        self.running = False
        
        # Отключаем клиент
        await self.client.disconnect()


async def main():
    """Функция запуска клиента"""
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description='Клиент игры "Код-Мастер"')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='Хост сервера (по умолчанию: localhost)')
    parser.add_argument('--port', type=int, default=8888, 
                        help='Порт сервера (по умолчанию: 8888)')
    
    args = parser.parse_args()
    
    # Создание и запуск интерфейса командной строки
    interface = ConsoleClientInterface(host=args.host, port=args.port)
    
    try:
        await interface.start()
    except Exception as e:
        logger.error(f"Ошибка при работе клиента: {e}")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nВыход из игры...")
        sys.exit(0)
