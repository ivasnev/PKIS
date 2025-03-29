import unittest
import threading
import time
import requests
import os
import sys
import subprocess
import signal
import socket
import os.path

# Исправляем импорт
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PR2.web_server import WebServer

class TestWebServer(unittest.TestCase):
    """Тестирование функциональности веб-сервера"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами - поиск свободного порта"""
        # Находим свободный порт
        cls.port = cls._find_free_port()
        
        # Получаем абсолютный путь к вспомогательному скрипту
        helper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_server_test_helper.py")
        print(f"Helper path: {helper_path}")
        
        # Запускаем сервер в отдельном процессе
        cmd = [sys.executable, helper_path, str(cls.port)]
        cls.server_process = subprocess.Popen(cmd)
        print(f"Started server process: {cls.server_process.pid} on port {cls.port}")
        
        # Даем время на запуск сервера
        time.sleep(3)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов - остановка сервера"""
        if hasattr(cls, 'server_process'):
            # Остановка процесса сервера
            print(f"Stopping server process: {cls.server_process.pid}")
            if sys.platform == 'win32':
                cls.server_process.kill()
            else:
                try:
                    cls.server_process.send_signal(signal.SIGTERM)
                    # Пытаемся дождаться завершения процесса
                    cls.server_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print("Сервер не остановился за отведенное время, принудительное завершение")
                    cls.server_process.kill()
                    cls.server_process.wait()
    
    @staticmethod
    def _find_free_port():
        """Находит свободный порт для запуска сервера"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def test_server_start_and_access(self):
        """Тест запуска сервера и доступа к нему"""
        try:
            # Проверяем доступность сервера
            response = requests.get(f"http://localhost:{self.port}/")
            self.assertEqual(response.status_code, 200)
            
            # Проверяем доступ к index.html
            self.assertIn("<html", response.text)
        except Exception as e:
            self.fail(f"Ошибка при проверке доступа к серверу: {e}")
    
    def test_server_not_found(self):
        """Тест обработки запроса к несуществующему ресурсу"""
        response = requests.get(f"http://localhost:{self.port}/not_exists.html")
        self.assertEqual(response.status_code, 404)
    
    def test_post_method(self):
        """Тест обработки POST-запроса"""
        response = requests.post(f"http://localhost:{self.port}/")
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

if __name__ == "__main__":
    unittest.main() 