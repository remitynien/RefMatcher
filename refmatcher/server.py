import http.server
import webbrowser
import urllib.parse
import urllib.request
import threading

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="refmatcher", **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

class OptimizeViewServer():
    def __init__(self, port: int, csv_path: str):
        self.port = port
        self.csv_path = csv_path
        self.httpd = None
        self.server_thread = threading.Thread(target=self._start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _start_server(self):
        # TODO: test if port is free (by catching OSError if no specific function allows port testing), if not use port 0 (port allocated by the OS)
        with http.server.HTTPServer(("", self.port), HTTPRequestHandler) as httpd:
            self.httpd = httpd
            webbrowser.open_new_tab(f"http://localhost:{self.port}?interval=1000&dir={urllib.parse.quote(self.csv_path)}")
            httpd.serve_forever()

    def shutdown(self):
        if self.httpd:
            self.httpd.shutdown()
            self.server_thread.join()
            self.httpd = None

    def __del__(self):
        self.shutdown()
