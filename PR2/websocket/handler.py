import json
import threading
from typing import Dict

import websockets

from websocket.analysis_service import FileAnalysisService
from websocket.interfaces import WebSocketHandlerInterface
from websocket.models import FileAnalysis, Stats


class WebSocketHandler(WebSocketHandlerInterface):
    """Обработчик WebSocket соединений"""

    def __init__(self, analysis_service: FileAnalysisService):
        """
        Инициализирует обработчик WebSocket

        Args:
            analysis_service: Сервис для анализа файлов
        """
        self.analysis_service = analysis_service
        # Хранилище результатов для каждого клиента
        self.client_results: Dict[websockets.WebSocketServerProtocol, Dict[str, FileAnalysis]] = {}
        self.results_lock = threading.Lock()

    async def handle_client(self, websocket, path):
        """
        Обрабатывает подключение клиента

        Args:
            websocket: WebSocket соединение
            path: Путь соединения
        """
        # Инициализируем хранилище результатов для нового клиента
        with self.results_lock:
            self.client_results[websocket] = {}

        try:
            await self._process_client_messages(websocket)
        except Exception:
            pass
        finally:
            # Очищаем результаты при отключении клиента
            with self.results_lock:
                if websocket in self.client_results:
                    del self.client_results[websocket]

    async def _process_client_messages(self, websocket):
        """
        Обрабатывает сообщения от клиента

        Args:
            websocket: WebSocket соединение
        """
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if data['type'] == 'files':
                    await self._handle_files_analysis(websocket, data)
                elif data['type'] == 'get_stats':
                    await self._send_stats(websocket)
                else:
                    await self.send_error(websocket, "Неизвестный тип сообщения")

            except json.JSONDecodeError:
                await self.send_error(websocket, "Неверный формат данных")

            except websockets.exceptions.ConnectionClosed:
                break

            except Exception as e:
                await self.send_error(websocket, "Внутренняя ошибка сервера")

    async def _handle_files_analysis(self, websocket, data: dict):
        """
        Обрабатывает анализ нескольких файлов

        Args:
            websocket: WebSocket соединение
            data: Данные запроса
        """
        try:
            files = data.get('files', [])
            if not files:
                await self.send_error(websocket, "Нет файлов для анализа")
                return

            # Параллельно анализируем все файлы
            analyses = await self.analysis_service.analyze_files(files)

            # Сохраняем результаты для конкретного клиента
            with self.results_lock:
                for analysis in analyses:
                    self.client_results[websocket][analysis.filename] = analysis

            # Отправляем результаты клиенту
            for analysis in analyses:
                await websocket.send(json.dumps(analysis.to_dict()))

        except Exception as e:
            await self.send_error(websocket, f"Ошибка при анализе файлов: {str(e)}")

    async def _send_stats(self, websocket):
        """
        Отправляет статистику клиенту

        Args:
            websocket: WebSocket соединение
        """
        try:
            with self.results_lock:
                client_results = self.client_results.get(websocket, {})

            # Подсчитываем статистику только для результатов конкретного клиента
            total_words = sum(r.word_count for r in client_results.values())
            total_chars = sum(r.char_count for r in client_results.values())
            total_lines = sum(r.line_count for r in client_results.values())
            total_files = len(client_results)

            stats = Stats(
                total_files=total_files,
                total_words=total_words,
                total_chars=total_chars,
                total_lines=total_lines
            )

            message = {
                'type': 'stats',
                'stats': stats.to_dict()
            }
            await websocket.send(json.dumps(message))

        except Exception as e:
            await self.send_error(websocket, f"Ошибка при получении статистики: {str(e)}")

    async def send_error(self, websocket, message: str):
        """
        Отправляет сообщение об ошибке клиенту

        Args:
            websocket: WebSocket соединение
            message: Сообщение об ошибке
        """
        try:
            error_message = {
                'type': 'error',
                'message': message
            }
            await websocket.send(json.dumps(error_message))
        except:
            pass