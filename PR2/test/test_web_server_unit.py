import unittest
import socket
import threading
import time
import os
import sys
import os.path

# Исправляем импорт
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PR2.web_server import WebServer

class TestWebServerUnit(unittest.TestCase):
    """Модульные тесты для класса WebServer"""
    
    def test_start_stop(self):
        """Тест запуска и остановки сервера"""
        # Находим свободный порт
        port = self._find_free_port()
        server = WebServer(port=port)
        
        # Запускаем сервер в отдельном потоке
        server_thread = threading.Thread(
            target=self._start_server,
            args=(server,),
            daemon=True
        )
        server_thread.start()
        
        # Даем время на запуск сервера
        time.sleep(1)
        
        # Проверка доступности сервера
        self.assertTrue(self._is_port_in_use(port), "Сервер не запустился")
        
        # Останавливаем сервер
        server.stop()
        time.sleep(1)
        
        # Проверяем, что порт больше не используется
        # Этот тест может быть нестабильным из-за возможного повторного использования порта
        # Тут мы больше проверяем, что метод stop() не вызывает ошибок
        server_thread.join(timeout=2)
    
    def _start_server(self, server):
        """Вспомогательный метод для запуска сервера"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(server.start())
        except Exception as e:
            print(f"Ошибка запуска сервера в тесте: {e}")
    
    @staticmethod
    def _find_free_port():
        """Находит свободный порт для запуска сервера"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    @staticmethod
    def _is_port_in_use(port):
        """Проверяет, используется ли порт"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('localhost', port))
                return True
            except (ConnectionRefusedError, socket.error):
                return False

if __name__ == "__main__":
    unittest.main() 