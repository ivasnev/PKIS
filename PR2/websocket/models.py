from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FileAnalysis:
    """Модель для хранения результатов анализа файла"""
    filename: str
    word_count: int
    char_count: int
    line_count: int

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для отправки клиенту"""
        return {
            'type': 'analysis',
            'filename': self.filename,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'line_count': self.line_count
        }


@dataclass
class Stats:
    """Модель для хранения общей статистики"""
    total_files: int
    total_words: int
    total_chars: int
    total_lines: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект статистики в словарь"""
        return {
            'total_files': self.total_files,
            'total_words': self.total_words,
            'total_chars': self.total_chars,
            'total_lines': self.total_lines,
            'average_words': self.total_words / self.total_files if self.total_files > 0 else 0,
            'average_chars': self.total_chars / self.total_files if self.total_files > 0 else 0,
            'average_lines': self.total_lines / self.total_files if self.total_files > 0 else 0
        } 