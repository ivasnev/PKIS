import asyncio
import signal
import sys
from typing import List

from PR2.http_server.server import HttpServer
from PR2.websocket.interfaces import ServerInterface
from PR2.websocket.server import WebSocketServer


class Application:
    """Основной класс приложения"""
    
    def __init__(self):
        """Инициализирует приложение"""
        self.servers: List[ServerInterface] = []
        self.running = False
        
    def setup_servers(self):
        """Настраивает серверы"""
        http_server = HttpServer(port=8000)
        websocket_server = WebSocketServer(port=8765)
        
        self.servers.append(http_server)
        self.servers.append(websocket_server)
        
    async def start(self):
        """Запускает все серверы"""
        self.running = True
        self.setup_servers()
        
        # Настраиваем обработчики сигналов для корректного завершения
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        
        # Запускаем все серверы
        server_tasks = []
        for server in self.servers:
            server_tasks.append(asyncio.create_task(server.start()))
        
        # Ждем завершения всех серверов (или прерывания)
        try:
            await asyncio.gather(*server_tasks)
        except asyncio.CancelledError:
            pass
        
    async def stop(self):
        """Останавливает все серверы"""
        if not self.running:
            return
            
        self.running = False
        print("\nЗавершение работы...")
        
        stop_tasks = []
        for server in self.servers:
            stop_tasks.append(asyncio.create_task(server.stop()))
        
        # Ждем остановки всех серверов
        await asyncio.gather(*stop_tasks)
        
        # Завершаем программу
        loop = asyncio.get_event_loop()
        loop.stop()


def main():
    """Точка входа в приложение"""
    try:
        app = Application()
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("\nПриложение остановлено пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main()) 