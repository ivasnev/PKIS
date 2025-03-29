import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List

import websockets


@dataclass
class FileAnalysis:
    filename: str
    word_count: int
    char_count: int
    line_count: int

    def to_dict(self) -> dict:
        return {
            'type': 'analysis',
            'filename': self.filename,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'line_count': self.line_count
        }

class AnalysisServer:
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        # Хранилище результатов для каждого клиента
        self.client_results: Dict[websockets.WebSocketServerProtocol, Dict[str, FileAnalysis]] = {}
        self.results_lock = threading.Lock()
        self.server = None
        self.server_task = None

    async def analyze_file(self, filename: str, content: str) -> FileAnalysis:
        """Анализирует содержимое файла в отдельном потоке"""
        def _analyze():
            lines = content.split('\n')
            words = content.split()
            return FileAnalysis(
                filename=filename,
                word_count=len(words),
                char_count=len(content),
                line_count=len(lines)
            )
        
        return await asyncio.get_event_loop().run_in_executor(
            self.thread_pool, _analyze
        )

    async def analyze_files(self, files: List[dict]) -> List[FileAnalysis]:
        """Параллельно анализирует несколько файлов"""
        tasks = []
        for file_data in files:
            task = self.analyze_file(file_data['filename'], file_data['content'])
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def handle_client(self, websocket, path):
        """Обрабатывает подключение клиента"""
        # Инициализируем хранилище результатов для нового клиента
        with self.results_lock:
            self.client_results[websocket] = {}
        
        try:
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data['type'] == 'files':
                        await self._handle_files_analysis(websocket, data)
                    elif data['type'] == 'get_stats':
                        await self._send_stats(websocket)
                    else:
                        await self._send_error(websocket, "Неизвестный тип сообщения")
                        
                except json.JSONDecodeError:
                    await self._send_error(websocket, "Неверный формат данных")
                    
                except websockets.exceptions.ConnectionClosed:
                    break
                    
                except Exception as e:
                    await self._send_error(websocket, "Внутренняя ошибка сервера")
                    
        except Exception:
            pass
        finally:
            # Очищаем результаты при отключении клиента
            with self.results_lock:
                if websocket in self.client_results:
                    del self.client_results[websocket]

    async def _handle_files_analysis(self, websocket, data: dict):
        """Обрабатывает анализ нескольких файлов"""
        try:
            files = data['files']
            if not files:
                await self._send_error(websocket, "Нет файлов для анализа")
                return

            # Параллельно анализируем все файлы
            analyses = await self.analyze_files(files)
            
            # Сохраняем результаты для конкретного клиента
            with self.results_lock:
                for analysis in analyses:
                    self.client_results[websocket][analysis.filename] = analysis
            
            # Отправляем результаты клиенту
            for analysis in analyses:
                await websocket.send(json.dumps(analysis.to_dict()))
            
        except Exception as e:
            await self._send_error(websocket, f"Ошибка при анализе файлов: {str(e)}")

    async def _send_stats(self, websocket):
        """Отправляет статистику клиенту"""
        try:
            with self.results_lock:
                client_results = self.client_results.get(websocket, {})
            
            # Подсчитываем статистику только для результатов конкретного клиента
            total_words = sum(r.word_count for r in client_results.values())
            total_chars = sum(r.char_count for r in client_results.values())
            total_lines = sum(r.line_count for r in client_results.values())
            total_files = len(client_results)
            
            stats = {
                'total_files': total_files,
                'total_words': total_words,
                'total_chars': total_chars,
                'total_lines': total_lines,
                'average_words': total_words / total_files if total_files > 0 else 0,
                'average_chars': total_chars / total_files if total_files > 0 else 0,
                'average_lines': total_lines / total_files if total_files > 0 else 0
            }
            
            message = {
                'type': 'stats',
                'stats': stats
            }
            await websocket.send(json.dumps(message))
        except Exception as e:
            await self._send_error(websocket, f"Ошибка при получении статистики: {str(e)}")

    async def _send_error(self, websocket, message: str):
        """Отправляет сообщение об ошибке клиенту"""
        try:
            error_message = {
                'type': 'error',
                'message': message
            }
            await websocket.send(json.dumps(error_message))
        except:
            pass

    async def start(self):
        """Запускает WebSocket-сервер"""
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        print(f"Сервер запущен на ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def stop(self):
        """Останавливает сервер"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("Сервер остановлен")

def main():
    """Точка входа в приложение"""
    try:
        server = AnalysisServer()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Сервер остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 