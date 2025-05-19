import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from websocket.interfaces import AnalysisInterface
from websocket.models import FileAnalysis


class FileAnalysisService(AnalysisInterface):
    """Сервис для анализа файлов"""
    
    def __init__(self, max_workers: int = 4):
        """
        Инициализирует сервис анализа файлов
        
        Args:
            max_workers: Максимальное количество рабочих потоков
        """
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    async def analyze_file(self, filename: str, content: str) -> FileAnalysis:
        """
        Анализирует содержимое файла в отдельном потоке
        
        Args:
            filename: Имя файла
            content: Содержимое файла
            
        Returns:
            Объект с результатами анализа
        """
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
        """
        Параллельно анализирует несколько файлов
        
        Args:
            files: Список словарей с данными файлов {'filename': '...', 'content': '...'}
            
        Returns:
            Список объектов с результатами анализа
        """
        tasks = []
        for file_data in files:
            task = self.analyze_file(file_data['filename'], file_data['content'])
            tasks.append(task)
        return await asyncio.gather(*tasks) 