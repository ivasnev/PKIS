import http.server

from http_server.interfaces import WebServerHandlerInterface


class HttpHandler(http.server.SimpleHTTPRequestHandler, WebServerHandlerInterface):
    """Обработчик HTTP-запросов"""

    def __init__(self, *args, **kwargs):
        """
        Инициализирует HTTP обработчик

        Args:
            *args: Позиционные аргументы для родительского класса
            **kwargs: Именованные аргументы для родительского класса
        """
        super().__init__(*args, directory="templates", **kwargs)

    def do_GET(self):
        """Обработка GET-запросов"""
        try:
            super().do_GET()
        except Exception:
            self.send_error(500)

    def do_POST(self):
        """Обработка POST-запросов"""
        self.send_error(405)