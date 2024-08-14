import http.server
import webbrowser
import threading
import shutil
from pathlib import Path
import refmatcher

MODULE_DIR = Path(refmatcher.__file__).parent

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

class OptimizeViewServer():
    def __init__(self, port: int, work_dir: str):
        self.port = port
        self.work_dir = work_dir
        self.httpd = None
        self._ensure_server_files()

    def _ensure_server_files(self):
        """Ensure that index.html, style.css and js are found in work_dir"""
        js_path = Path(self.work_dir) / "js"
        js_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(MODULE_DIR / "index.html", self.work_dir)
        shutil.copy(MODULE_DIR / "style.css", self.work_dir)
        shutil.copytree(MODULE_DIR / "js", js_path, dirs_exist_ok = True)

    def _start_server(self):
        # TODO: test if port is free (by catching OSError if no specific function allows port testing), if not use port 0 (port allocated by the OS)
        with http.server.HTTPServer(("", self.port),
                                    lambda *args, **kwargs: HTTPRequestHandler(*args, directory=self.work_dir, **kwargs)
                                    )as httpd:
            self.httpd = httpd
            # TODO: add opening tab option in addon preferences
            webbrowser.open_new_tab(f"http://localhost:{self.port}?interval=1000")
            httpd.serve_forever()

    def start(self):
        if not self.httpd: # would need a mutex for multipurpose use case, not needed for the usage of the addon
            self.server_thread = threading.Thread(target=self._start_server)
            self.server_thread.daemon = True
            self.server_thread.start()

    def shutdown(self):
        if self.httpd:
            self.httpd.shutdown()
            self.server_thread.join()
            self.httpd = None

    def __del__(self):
        self.shutdown()
