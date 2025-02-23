import unittest
import os
from unittest.mock import patch

from main import process_file, main


class TestTextProcessing(unittest.TestCase):
    def setUp(self):
        """Создаёт временные файлы для тестирования."""
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write("Hello world! Hello everyone.\nHello again.")

        with open("empty.txt", "w", encoding="utf-8") as f:
            pass  # Создаём пустой файл

        with open("case.txt", "w", encoding="utf-8") as f:
            f.write("Python python PYTHON\npython")

    def tearDown(self):
        """Удаляет временные файлы после тестов."""
        for filename in ["test.txt", "empty.txt", "case.txt", "no_access.txt"]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_process_text(self):
        self.assertEqual(process_file("test.txt", "Hello"), (6, 3))
        self.assertEqual(process_file("test.txt", "world"), (6, 1))
        self.assertEqual(process_file("test.txt", "everyone"), (6, 1))
        self.assertEqual(process_file("test.txt", "Python"), (6, 0))

    def test_empty_file(self):
        self.assertEqual(process_file("empty.txt", "test"), (0, 0))

    def test_case_insensitivity(self):
        self.assertEqual(process_file("case.txt", "python"), (4, 4))

    def test_file_not_found(self):
        """Тест обработки ошибки, если файл отсутствует."""
        with patch('builtins.print') as mocked_print:
            with self.assertRaises(SystemExit) as cm:
                process_file("nonexistent.txt", "test")

            # Проверяем, что print был вызван с правильными параметрами
            mocked_print.assert_any_call("Ошибка: файл не найден.")
        self.assertEqual(cm.exception.code, 1)

    def test_file_permission_error(self):
        """Тест обработки ошибки доступа к файлу."""
        with open("no_access.txt", "w", encoding="utf-8") as f:
            f.write("This is a test file.")
        os.chmod("no_access.txt", 0o000)  # Запрещаем доступ

        try:
            with patch('builtins.print') as mocked_print:
                with self.assertRaises(SystemExit) as cm:
                    process_file("no_access.txt", "test")
                mocked_print.assert_any_call("Ошибка: [Errno 13] Permission denied: 'no_access.txt'")
            self.assertEqual(cm.exception.code, 1)
        finally:
            os.chmod("no_access.txt", 0o644)  # Возвращаем права

class TestMainFunction(unittest.TestCase):

    @patch('sys.argv', ['script.py', 'test_file.txt', 'word'])
    @patch('main.process_file')  # Патчим process_file
    def test_main(self, mock_process_file):
        # Настроим mock, чтобы process_file возвращал нужные данные
        mock_process_file.return_value = (100, 10)

        with patch('builtins.print') as mocked_print:
            main()  # Вызываем основную функцию

            # Проверяем, что print был вызван с правильными параметрами
            mocked_print.assert_any_call("Общее количество слов в файле: 100")
            mocked_print.assert_any_call("Количество повторений слова 'word': 10")

    @patch('sys.argv', ['script.py', 'test_file.txt'])
    @patch('sys.exit')  # Патчим sys.exit, чтобы предотвратить завершение программы
    @patch('builtins.print')  # Патчим print, чтобы проверять его вызовы
    def test_main_not_enough_args(self, mocked_print, mocked_exit):
        main()  # Вызываем основную функцию

        # Проверяем, что print был вызван с правильными параметрами
        mocked_print.assert_any_call("Использование: python script.py <путь_к_файлу> <слово_для_поиска>")

if __name__ == '__main__':
    unittest.main()
