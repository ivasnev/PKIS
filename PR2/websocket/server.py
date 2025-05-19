import websockets

from websocket.analysis_service import FileAnalysisService
from websocket.interfaces import ServerInterface
from websocket.handler import WebSocketHandler

class WebSocketServer(ServerInterface):
    """Сервер для обработки WebSocket соединений"""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        """
        Инициализирует WebSocket сервер
        
        Args:
            host: Хост для привязки сервера
            port: Порт для привязки сервера
        """
        self.host = host
        self.port = port
        self.analysis_service = FileAnalysisService()
        self.handler = WebSocketHandler(self.analysis_service)
        self.server = None
    
    async def start(self):
        """Запускает WebSocket-сервер"""
        self.server = await websockets.serve(
            self.handler.handle_client,
            self.host,
            self.port
        )
        print(f"WebSocket сервер запущен на http://{self.host}:{self.port}")
        await self.server.wait_closed()
    
    async def stop(self):
        """Останавливает сервер"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket сервер остановлен") 