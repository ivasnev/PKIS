import unittest
import os
from unittest.mock import patch, MagicMock

from main import (
    SimpleTextProcessor,
    RegexTextProcessor,
    TextProcessorFactory,
    TextAnalyzer,
    ITextProcessor,
    main
)


class TestTextProcessing(unittest.TestCase):
    def setUp(self):
        """Создаёт временные файлы для тестирования."""
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write("Hello world! Hello everyone.\nHello again.")

        with open("empty.txt", "w", encoding="utf-8") as f:
            pass  # Создаём пустой файл

        with open("case.txt", "w", encoding="utf-8") as f:
            f.write("Python python PYTHON\npython")

        with open("special.txt", "w", encoding="utf-8") as f:
            f.write("cat cats cat's cat's cat's\ncat")

    def tearDown(self):
        """Удаляет временные файлы после тестов."""
        for filename in ["test.txt", "empty.txt", "case.txt", "no_access.txt", "special.txt"]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_process_text_simple(self):
        processor = SimpleTextProcessor()
        analyzer = TextAnalyzer(processor)
        
        total_words, word_count = analyzer.analyze_file("test.txt", "Hello")
        self.assertEqual((total_words, word_count), (6, 3))
        
        total_words, word_count = analyzer.analyze_file("test.txt", "world")
        self.assertEqual((total_words, word_count), (6, 1))
        
        total_words, word_count = analyzer.analyze_file("test.txt", "everyone")
        self.assertEqual((total_words, word_count), (6, 1))
        
        total_words, word_count = analyzer.analyze_file("test.txt", "Python")
        self.assertEqual((total_words, word_count), (6, 0))

    def test_process_text_regex(self):
        """Тест обработки текста с использованием регулярных выражений."""
        processor = RegexTextProcessor({"encoding": "utf-8", "case_sensitive": False})
        total_words, word_count = processor.process_text("Python is a programming language. Python is great!", "python")
        self.assertEqual(total_words, 8)
        self.assertEqual(word_count, 2)

    def test_empty_file(self):
        for processor in [SimpleTextProcessor(), RegexTextProcessor()]:
            analyzer = TextAnalyzer(processor)
            total_words, word_count = analyzer.analyze_file("empty.txt", "test")
            self.assertEqual((total_words, word_count), (0, 0))

    def test_case_insensitivity(self):
        for processor in [SimpleTextProcessor(), RegexTextProcessor()]:
            analyzer = TextAnalyzer(processor)
            total_words, word_count = analyzer.analyze_file("case.txt", "python")
            self.assertEqual((total_words, word_count), (4, 4))

    def test_file_not_found(self):
        """Тест обработки ошибки, если файл отсутствует."""
        for processor in [SimpleTextProcessor(), RegexTextProcessor()]:
            analyzer = TextAnalyzer(processor)
            with patch('builtins.print') as mocked_print:
                with self.assertRaises(SystemExit) as cm:
                    analyzer.analyze_file("nonexistent.txt", "test")
                mocked_print.assert_any_call("Ошибка: файл не найден.")
            self.assertEqual(cm.exception.code, 1)

    def test_file_permission_error(self):
        """Тест обработки ошибки доступа к файлу."""
        processor = SimpleTextProcessor()
        analyzer = TextAnalyzer(processor)
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(SystemExit):
                analyzer.analyze_file("no_access.txt", "test")


class TestTextProcessorFactory(unittest.TestCase):
    def test_create_processor(self):
        # Тест создания простого процессора
        processor = TextProcessorFactory.create_processor("simple")
        self.assertIsInstance(processor, SimpleTextProcessor)
        
        # Тест создания процессора с регулярными выражениями
        processor = TextProcessorFactory.create_processor("regex")
        self.assertIsInstance(processor, RegexTextProcessor)
        
        # Тест с конфигурацией
        config = {"punctuation": ".,", "encoding": "utf-8"}
        processor = TextProcessorFactory.create_processor("simple", config)
        self.assertEqual(processor.config["punctuation"], ".,")
        self.assertEqual(processor.config["encoding"], "utf-8")
        
        # Тест с неверным типом процессора
        with self.assertRaises(ValueError):
            TextProcessorFactory.create_processor("unknown")


class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_processor = MagicMock(spec=ITextProcessor)
        self.analyzer = TextAnalyzer(self.mock_processor)

    def test_analyze_file(self):
        self.mock_processor.process_file.return_value = (100, 10)
        total_words, word_count = self.analyzer.analyze_file("test.txt", "word")
        
        self.assertEqual((total_words, word_count), (100, 10))
        self.mock_processor.process_file.assert_called_once_with("test.txt", "word")

    def test_print_results(self):
        with patch('builtins.print') as mocked_print:
            self.analyzer.print_results(100, 10, "word")
            mocked_print.assert_any_call("Общее количество слов в файле: 100")
            mocked_print.assert_any_call("Количество повторений слова 'word': 10")


class TestMain(unittest.TestCase):
    def setUp(self):
        """Создаёт временные файлы для тестирования."""
        self.test_files = [
            "test.txt",
            "empty.txt",
            "case.txt",
            "special.txt",
            "punctuation.txt",
            "forms.txt",
            "spaces.txt",
            "no_access.txt"
        ]
        
        # Создаем тестовые файлы
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write("Hello world! Hello everyone.\nHello again.")

        with open("empty.txt", "w", encoding="utf-8") as f:
            pass

        with open("case.txt", "w", encoding="utf-8") as f:
            f.write("Python python PYTHON\npython")

        with open("special.txt", "w", encoding="utf-8") as f:
            f.write("cat cats cat's cat's cat's\ncat")

        with open("punctuation.txt", "w", encoding="utf-8") as f:
            f.write("word, word. word! word? word; word: word")

        with open("forms.txt", "w", encoding="utf-8") as f:
            f.write("cat cats cat's cat's cat's\ncat")

        with open("spaces.txt", "w", encoding="utf-8") as f:
            f.write("word  word   word\nword")

    def tearDown(self):
        """Удаляет временные файлы после тестов."""
        for filename in self.test_files:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except PermissionError:
                    # Если файл защищен от записи, пробуем изменить права
                    os.chmod(filename, 0o644)
                    os.remove(filename)

    def test_main_simple(self):
        """Тест запуска с простым процессором"""
        with patch('sys.argv', ['script.py', 'test.txt', 'test', 'simple']), \
             patch('main.TextProcessorFactory') as mock_factory, \
             patch('main.TextAnalyzer') as mock_analyzer:
            mock_processor = MagicMock()
            mock_factory.create_processor.return_value = mock_processor
            mock_analyzer.return_value.analyze_file.return_value = (10, 2)
            
            main()
            
            mock_factory.create_processor.assert_called_once_with("simple")
            mock_analyzer.assert_called_once_with(mock_processor)
            mock_analyzer.return_value.analyze_file.assert_called_once_with("test.txt", "test")
            mock_analyzer.return_value.print_results.assert_called_once_with(10, 2, "test")

    def test_main_regex(self):
        """Тест запуска с процессором регулярных выражений"""
        with patch('sys.argv', ['script.py', 'test.txt', 'test', 'regex']), \
             patch('main.TextProcessorFactory') as mock_factory, \
             patch('main.TextAnalyzer') as mock_analyzer:
            mock_processor = MagicMock()
            mock_factory.create_processor.return_value = mock_processor
            mock_analyzer.return_value.analyze_file.return_value = (10, 2)
            
            main()
            
            mock_factory.create_processor.assert_called_once_with("regex")
            mock_analyzer.assert_called_once_with(mock_processor)
            mock_analyzer.return_value.analyze_file.assert_called_once_with("test.txt", "test")
            mock_analyzer.return_value.print_results.assert_called_once_with(10, 2, "test")

    @patch('sys.argv', ['script.py'])
    @patch('builtins.print')
    def test_main_no_args(self, mock_print):
        """Тест запуска без аргументов"""
        main()
        mock_print.assert_called_once_with("Использование: python script.py <путь_к_файлу> <слово_для_поиска> [тип_процессора]")

    @patch('sys.argv', ['script.py', 'test.txt'])
    @patch('builtins.print')
    def test_main_missing_word(self, mock_print):
        """Тест запуска без слова для поиска"""
        main()
        mock_print.assert_called_once_with("Использование: python script.py <путь_к_файлу> <слово_для_поиска> [тип_процессора]")

    def test_main_invalid_processor(self):
        """Тест запуска с неверным типом процессора"""
        with patch('sys.argv', ['script.py', 'test.txt', 'test', 'unknown']):
            with self.assertRaises(ValueError) as cm:
                main()
            self.assertEqual(str(cm.exception), "Неизвестный тип процессора: unknown")


if __name__ == '__main__':
    unittest.main()
