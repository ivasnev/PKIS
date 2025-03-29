# Тестирование веб-сервера

## Общая структура тестов

```mermaid
graph TD
    A[Тесты веб-сервера] --> B[Интеграционные тесты]
    A --> C[Модульные тесты]
    
    B --> D[test_web_server.py]
    D --> D1[Запуск сервера]
    D --> D2[HTTP запросы]
    D --> D3[Проверка ответов]
    
    C --> E[test_web_server_unit.py]
    E --> E1[Запуск/остановка]
    E --> E2[Проверка портов]
    E --> E3[Асинхронные операции]
```

## Процесс интеграционного тестирования

```mermaid
sequenceDiagram
    participant Test as test_web_server.py
    participant Helper as web_server_test_helper.py
    participant Server as WebServer
    
    Test->>Test: Находит свободный порт
    Test->>Helper: Запускает процесс
    Helper->>Helper: Устанавливает рабочую директорию
    Helper->>Server: Создает экземпляр WebServer
    Server->>Server: Запускает HTTP сервер
    
    Note over Test,Server: Тесты HTTP запросов
    
    Test->>Server: GET / (200 OK)
    Test->>Server: GET /not_exists.html (404)
    Test->>Server: POST / (405)
    
    Test->>Helper: Отправляет SIGTERM
    Helper->>Server: Останавливает сервер
    Server-->>Test: Завершение процесса
```

## Процесс модульного тестирования

```mermaid
sequenceDiagram
    participant Test as test_web_server_unit.py
    participant Server as WebServer
    participant Thread as Server Thread
    
    Test->>Test: Находит свободный порт
    Test->>Server: Создает экземпляр
    Test->>Thread: Запускает сервер в потоке
    Thread->>Server: Запускает HTTP сервер
    
    Note over Test,Server: Проверка доступности
    
    Test->>Server: Проверяет порт
    Server-->>Test: Порт активен
    
    Test->>Server: Останавливает сервер
    Server-->>Test: Сервер остановлен
```

## Структура файлов

```mermaid
graph LR
    A[PR2/test/] --> B[test_web_server.py]
    A --> C[web_server_test_helper.py]
    A --> D[test_web_server_unit.py]
    
    B --> E[Интеграционные тесты]
    C --> F[Вспомогательный скрипт]
    D --> G[Модульные тесты]
```

## Описание тестов

### Интеграционные тесты (test_web_server.py)

Тесты проверяют полный цикл работы веб-сервера:
- Запуск сервера в отдельном процессе
- Обработка HTTP запросов
- Корректность ответов
- Завершение работы

Основные проверки:
- GET запрос к корневому пути (200 OK)
- GET запрос к несуществующему файлу (404)
- POST запрос (405 Method Not Allowed)

### Модульные тесты (test_web_server_unit.py)

Тесты проверяют внутреннюю функциональность класса WebServer:
- Запуск сервера
- Проверка доступности порта
- Остановка сервера
- Асинхронные операции

### Вспомогательный скрипт (web_server_test_helper.py)

Скрипт для запуска сервера в отдельном процессе:
- Установка рабочей директории
- Обработка сигналов завершения
- Запуск сервера с указанным портом

## Запуск тестов

### Запуск всех тестов
```bash
python3 -m unittest discover -p "test_web_server*.py" -s PR2/test
```

### Запуск интеграционных тестов
```bash
python3 -m PR2.test.test_web_server
```

### Запуск модульных тестов
```bash
python3 -m PR2.test.test_web_server_unit
```

## Требования к окружению

- Python 3.9+
- Библиотека requests
- Доступ к портам (динамическое выделение)
- Директория templates с index.html 