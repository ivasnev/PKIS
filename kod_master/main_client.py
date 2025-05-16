#!/usr/bin/env python3
import asyncio
import argparse
import logging
import sys
from client.client import GameClient
from client.console_interface import ConsoleInterface

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Функция запуска клиента"""
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description='Клиент игры "Код-Мастер"')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='Хост сервера (по умолчанию: localhost)')
    parser.add_argument('--port', type=int, default=8888, 
                        help='Порт сервера (по умолчанию: 8888)')
    
    args = parser.parse_args()
    
    # Создание клиента и интерфейса
    client = GameClient(host=args.host, port=args.port)
    interface = ConsoleInterface(client)
    
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
