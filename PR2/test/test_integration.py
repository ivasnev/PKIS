import asyncio
import json
import sys
from pathlib import Path

import pytest
import pytest_asyncio
import websockets

# Добавляем путь к директории с сервером
sys.path.append(str(Path(__file__).parent))
from PR2.server import AnalysisServer

# Путь к тестовым файлам
TEST_FILES_DIR = Path(__file__).parent / 'test_files'
TEST_FILES = [
    'test1.txt',
    'test2.txt',
    'test3.txt'
]


@pytest_asyncio.fixture
async def server():
    """Фикстура для запуска сервера один раз за сессию"""
    print("Запуск сервера")
    server = AnalysisServer(host='localhost', port=8765)
    server_task = asyncio.create_task(server.start())
    # Даем серверу время на запуск
    await asyncio.sleep(1)
    yield server
    # Останавливаем сервер
    print("Остановка сервера")
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


def read_test_file(filename):
    """Читает содержимое тестового файла"""
    with open(TEST_FILES_DIR / filename, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.mark.asyncio
async def test_server_connection(server):
    """Тест подключения к серверу"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        assert websocket.open


@pytest.mark.asyncio
async def test_single_file_analysis(server):
    """Тест анализа одного файла"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Читаем тестовый файл
        content = read_test_file('test1.txt')
    
        # Отправляем файл на анализ
        message = {
            'type': 'files',
            'files': [{
                'filename': 'test1.txt',
                'content': content
            }]
        }
        await websocket.send(json.dumps(message))

        # Получаем результат
        response = await websocket.recv()
        data = json.loads(response)
    
        # Проверяем результат
        assert data['type'] == 'analysis'
        assert data['filename'] == 'test1.txt'
        assert data['word_count'] > 0
        assert data['char_count'] > 0
        assert data['line_count'] > 0


@pytest.mark.asyncio
async def test_multiple_files_analysis(server):
    """Тест анализа нескольких файлов"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Читаем все тестовые файлы
        files_data = []
        for filename in TEST_FILES:
            content = read_test_file(filename)
            files_data.append({
                'filename': filename,
                'content': content
            })

        # Отправляем файлы на анализ
        message = {
            'type': 'files',
            'files': files_data
        }
        await websocket.send(json.dumps(message))

        # Получаем результаты для каждого файла
        results = []
        for _ in range(len(TEST_FILES)):
            response = await websocket.recv()
            data = json.loads(response)
            assert data['type'] == 'analysis'
            results.append(data)

        # Проверяем, что получили результаты для всех файлов
        assert len(results) == len(TEST_FILES)

        # Проверяем, что все файлы были проанализированы
        filenames = {r['filename'] for r in results}
        assert filenames == set(TEST_FILES)


@pytest.mark.asyncio
async def test_get_stats(server):
    """Тест получения статистики"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Сначала анализируем файлы
        files_data = []
        for filename in TEST_FILES:
            content = read_test_file(filename)
            files_data.append({
                'filename': filename,
                'content': content
            })

        await websocket.send(json.dumps({
            'type': 'files',
            'files': files_data
        }))

        # Получаем результаты анализа
        for _ in range(len(TEST_FILES)):
            await websocket.recv()

        # Запрашиваем статистику
        await websocket.send(json.dumps({'type': 'get_stats'}))

        # Получаем статистику
        response = await websocket.recv()
        data = json.loads(response)

        # Проверяем статистику
        assert data['type'] == 'stats'
        stats = data['stats']
        assert stats['total_files'] == len(TEST_FILES)
        assert stats['total_words'] > 0
        assert stats['total_chars'] > 0
        assert stats['total_lines'] > 0
        assert stats['average_words'] > 0
        assert stats['average_chars'] > 0
        assert stats['average_lines'] > 0


@pytest.mark.asyncio
async def test_invalid_message(server):
    """Тест обработки некорректного сообщения"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Отправляем некорректное сообщение
        await websocket.send(json.dumps({
            'type': 'invalid_type',
            'data': 'some data'
        }))

        # Получаем сообщение об ошибке
        response = await websocket.recv()
        data = json.loads(response)

        assert data['type'] == 'error'
        assert 'Неизвестный тип сообщения' in data['message']


@pytest.mark.asyncio
async def test_invalid_json(server):
    """Тест обработки некорректного JSON"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Отправляем некорректный JSON
        await websocket.send('invalid json')

        # Получаем сообщение об ошибке
        response = await websocket.recv()
        data = json.loads(response)

        assert data['type'] == 'error'
        assert 'Неверный формат данных' in data['message']


@pytest.mark.asyncio
async def test_empty_file(server):
    """Тест анализа пустого файла"""
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Отправляем пустой файл
        message = {
            'type': 'files',
            'files': [{
                'filename': 'empty.txt',
                'content': ''
            }]
        }
        await websocket.send(json.dumps(message))

        # Получаем результат
        response = await websocket.recv()
        data = json.loads(response)

        # Проверяем результат
        assert data['type'] == 'analysis'
        assert data['filename'] == 'empty.txt'
        assert data['word_count'] == 0
        assert data['char_count'] == 0
        assert data['line_count'] == 1  # Пустой файл считается как одна строка
