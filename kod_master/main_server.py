#!/usr/bin/env python3
import asyncio
import argparse
import logging
from server.server import GameServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Функция запуска сервера"""
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description='Сервер игры "Код-Мастер"')
    parser.add_argument('--host', type=str, default='0.0.0.0', 
                        help='Хост для прослушивания (по умолчанию: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8888, 
                        help='Порт для прослушивания (по умолчанию: 8888)')
    parser.add_argument('--min-players', type=int, default=2, 
                        help='Минимальное количество игроков (по умолчанию: 2)')
    parser.add_argument('--max-players', type=int, default=4, 
                        help='Максимальное количество игроков (по умолчанию: 4)')
    parser.add_argument('--code-length', type=int, default=4, 
                        help='Длина секретного кода (по умолчанию: 4)')
    parser.add_argument('--attempts', type=int, default=10, 
                        help='Максимальное количество попыток (по умолчанию: 10)')
    
    args = parser.parse_args()
    
    # Создание и запуск сервера
    server = GameServer(
        host=args.host,
        port=args.port,
        min_players=args.min_players,
        max_players=args.max_players,
        code_length=args.code_length,
        allowed_attempts=args.attempts
    )
    
    try:
        logger.info("Запуск сервера...")
        await server.start()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")

if __name__ == "__main__":
    asyncio.run(main())
