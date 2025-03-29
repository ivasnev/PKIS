import asyncio
import http.server
import socketserver


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик HTTP-запросов"""
    
    def __init__(self, *args, **kwargs):
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

class WebServer:
    """Класс для управления веб-сервером"""
    
    def __init__(self, host: str = "", port: int = 8000):
        self.host = host
        self.port = port
        self.httpd = None

    async def start(self):
        """Запускает веб-сервер"""
        try:
            self.httpd = socketserver.TCPServer(
                (self.host, self.port),
                CustomHandler
            )
            print(f"Веб-сервер запущен на http://{self.host or 'localhost'}:{self.port}")
            self.httpd.serve_forever()
        except Exception as e:
            print(f"Ошибка при запуске веб-сервера: {e}")

    def stop(self):
        """Останавливает веб-сервер"""
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
                print("Веб-сервер остановлен")
            except:
                pass

def main():
    """Точка входа в приложение"""
    try:
        server = WebServer()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Сервер остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 