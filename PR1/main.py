from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import sys
from pathlib import Path
import re


class ITextProcessor(ABC):
    """Интерфейс для обработки текста"""
    
    @abstractmethod
    def process_text(self, text: str, search_word: str) -> Tuple[int, int]:
        """Обработка текста"""
        pass
    
    @abstractmethod
    def process_file(self, file_path: str, search_word: str) -> Tuple[int, int]:
        """Обработка файла"""
        pass


class SimpleTextProcessor(ITextProcessor):
    """Простой процессор текста"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "punctuation": ".,!?;:()\"'",
            "encoding": "utf-8"
        }
    
    def process_text(self, text: str, search_word: str) -> Tuple[int, int]:
        total_words = 0
        word_count = 0
        search_word_lower = search_word.lower()
        
        for word in text.split():
            clean_word = word.strip(self.config["punctuation"]).lower()
            if clean_word:
                total_words += 1
                word_count += clean_word == search_word_lower
                
        return total_words, word_count
    
    def process_file(self, file_path: str, search_word: str) -> Tuple[int, int]:
        try:
            with open(file_path, 'r', encoding=self.config["encoding"]) as file:
                text = file.read()
                return self.process_text(text, search_word)
        except FileNotFoundError:
            print("Ошибка: файл не найден.")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)


class RegexTextProcessor(ITextProcessor):
    """Процессор текста с использованием регулярных выражений"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "encoding": "utf-8",
            "case_sensitive": False
        }
    
    def process_text(self, text: str, search_word: str) -> Tuple[int, int]:
        # Подсчитываем общее количество слов (исключая пунктуацию)
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        
        # Создаем регулярное выражение для поиска слова
        if self.config["case_sensitive"]:
            pattern = r'\b' + re.escape(search_word) + r'\b'
        else:
            pattern = r'\b' + re.escape(search_word.lower()) + r'\b'
            text = text.lower()
        
        # Ищем все вхождения слова
        matches = re.findall(pattern, text)
        word_count = len(matches)
        
        return total_words, word_count
    
    def process_file(self, file_path: str, search_word: str) -> Tuple[int, int]:
        try:
            with open(file_path, 'r', encoding=self.config["encoding"]) as file:
                text = file.read()
                return self.process_text(text, search_word)
        except FileNotFoundError:
            print("Ошибка: файл не найден.")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)


class TextProcessorFactory:
    """Фабрика для создания процессоров текста"""
    
    @staticmethod
    def create_processor(processor_type: str = "simple", config: Dict[str, Any] = None) -> ITextProcessor:
        if processor_type == "simple":
            return SimpleTextProcessor(config)
        elif processor_type == "regex":
            return RegexTextProcessor(config)
        raise ValueError(f"Неизвестный тип процессора: {processor_type}")


class TextAnalyzer:
    """Основной класс для анализа текста"""
    
    def __init__(self, processor: ITextProcessor):
        self.processor = processor
    
    def analyze_file(self, file_path: str, search_word: str) -> Tuple[int, int]:
        return self.processor.process_file(file_path, search_word)
    
    def print_results(self, total_words: int, word_count: int, search_word: str):
        print(f"Общее количество слов в файле: {total_words}")
        print(f"Количество повторений слова '{search_word}': {word_count}")


def main():
    """Основная функция для обработки входных параметров и вызова функций."""
    if len(sys.argv) < 3:
        print("Использование: python script.py <путь_к_файлу> <слово_для_поиска> [тип_процессора]")
        return

    file_path = sys.argv[1]
    search_word = sys.argv[2]
    processor_type = sys.argv[3] if len(sys.argv) > 3 else "simple"
    
    processor = TextProcessorFactory.create_processor(processor_type)
    analyzer = TextAnalyzer(processor)
    
    total_words, word_count = analyzer.analyze_file(file_path, search_word)
    analyzer.print_results(total_words, word_count, search_word)


if __name__ == "__main__":
    main()
