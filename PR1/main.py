import sys
from typing import Tuple

def process_file(file_path: str, search_word: str) -> Tuple[int, int]:
    """
    Обрабатывает файл построчно, подсчитывая общее количество слов и количество вхождений искомого слова.
    :param file_path: Путь к файлу
    :param search_word: Слово для поиска
    :return: Кортеж (общее количество слов, количество повторений слова)
    """
    total_words = 0
    word_count = 0
    search_word_lower = search_word.lower()
    punctuation = ".,!?;:()\"'"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                for word in line.split():
                    clean_word = word.strip(punctuation).lower()
                    if clean_word:
                        total_words += 1
                        word_count += clean_word == search_word_lower
    except FileNotFoundError:
        print("Ошибка: файл не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    return total_words, word_count

def main():
    """
    Основная функция для обработки входных параметров и вызова функций.
    """
    if len(sys.argv) < 3:
        print("Использование: python script.py <путь_к_файлу> <слово_для_поиска>")
        return

    file_path = sys.argv[1]
    search_word = sys.argv[2]
    total_words, word_count = process_file(file_path, search_word)

    print(f"Общее количество слов в файле: {total_words}")
    print(f"Количество повторений слова '{search_word}': {word_count}")

if __name__ == "__main__":
    main()
