import http.server
import webbrowser
import threading
import shutil
from pathlib import Path
import json
from typing import Callable

MODULE_DIR = Path(__file__).parent

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, live_data_callback: Callable[[], dict], stop_callback: Callable[[], None], *args, **kwargs):
        self.live_data_callback = live_data_callback
        self.stop_callback = stop_callback
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        elif self.path == "/data":
            data = self.live_data_callback()
            json_data = json.dumps(data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json_data.encode())
            return
        elif self.path == "/stop":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Stopping optimization...")
            self.stop_callback()
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format: str, *args) -> None:
        # override log function to remove console logs
        pass

class OptimizeViewServer():
    def __init__(self, port: int, work_dir: str, live_data_callback: Callable[[], dict], stop_callback: Callable[[], None]):
        self.port = port
        self.work_dir = work_dir
        self.httpd = None
        self.live_data_callback = live_data_callback
        self.stop_callback = stop_callback
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
                                    lambda *args, **kwargs: HTTPRequestHandler(
                                        self.live_data_callback,
                                        self.stop_callback,
                                        *args,
                                        directory=self.work_dir,
                                        **kwargs)
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

if __name__ == "__main__":
    # debug server
    import os
    print("Create server object")
    data_callback = lambda : {"field 1": 1, "field 2": 222, "field 3": "three"}
    stop_callback = lambda : print("Stop requested")
    server = OptimizeViewServer(8001, os.path.join(os.path.curdir, "server_dir"), data_callback, stop_callback)
    print("Start server")
    server.start()
    input("Press Enter to shutdown...\n")
    print("Shutdown server")
    server.shutdown()
    print("Done")