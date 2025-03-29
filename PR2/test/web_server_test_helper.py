#!/usr/bin/env python3
"""
Вспомогательный скрипт для запуска веб-сервера в тестах
"""
import asyncio
import sys
import signal
import os
import os.path

# Исправляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PR2.web_server import WebServer

# Переходим в директорию PR2 для корректной работы с файлами
pr2_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(pr2_dir)

# Создаем функцию для корректного завершения
def shutdown(signum=None, frame=None):
    """Корректно завершает работу сервера"""
    if 'server' in globals():
        server.stop()
    sys.exit(0)

# Регистрация обработчиков сигналов
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# Получаем порт из аргументов командной строки
port = 8080
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f"Некорректный порт: {sys.argv[1]}, используется порт по умолчанию: {port}")

print(f"Рабочая директория: {os.getcwd()}")
print(f"Запуск тестового сервера на порту: {port}")

# Инициализируем и запускаем сервер
try:
    server = WebServer(port=port)
    asyncio.run(server.start())
except KeyboardInterrupt:
    shutdown()
except Exception as e:
    print(f"Ошибка в работе тестового сервера: {e}")
    sys.exit(1) 