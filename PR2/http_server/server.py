import asyncio
import socketserver
from concurrent.futures import ThreadPoolExecutor

from http_server.interfaces import ServerInterface

from http_server.handler import HttpHandler


class HttpServer(ServerInterface):
    """Класс для управления HTTP сервером"""
    
    def __init__(self, host: str = "", port: int = 8000):
        """
        Инициализирует HTTP сервер
        
        Args:
            host: Хост для привязки сервера
            port: Порт для привязки сервера
        """
        self.host = host
        self.port = port
        self.httpd = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def start(self):
        """Запускает HTTP-сервер"""
        loop = asyncio.get_event_loop()
        
        try:
            self.httpd = socketserver.TCPServer(
                (self.host, self.port),
                HttpHandler
            )
            print(f"HTTP сервер запущен на http://{self.host or 'localhost'}:{self.port}")
            
            # Запускаем сервер в отдельном потоке, чтобы не блокировать event loop
            await loop.run_in_executor(
                self._executor,
                self.httpd.serve_forever
            )
            
        except Exception as e:
            print(f"Ошибка при запуске HTTP сервера: {e}")

    async def stop(self):
        """Останавливает HTTP-сервер"""
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
                self._executor.shutdown(wait=False)
                print("HTTP сервер остановлен")
            except:
                pass 