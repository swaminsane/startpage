
# ===== STARTPAGE SERVER (FINAL) =====
# Features:
# - Serve index.html
# - Fast file search (plocate)
# - Run scripts from ~/.local/bin

from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import json
import os

# ===== 🔧 EDIT THIS =====
SEARCH_ROOT = os.path.expanduser("~")  # search inside your home

class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/search"):
            self.handle_search()
            return

        if self.path.startswith("/run"):
            self.handle_run()
            return

        return super().do_GET()

    # ===== FILE SEARCH =====
    def handle_search(self):
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            term = params.get("q", [""])[0]

            term = term.replace('"', '').replace("'", "")

            result = subprocess.run(
                ["locate", term],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            files = result.stdout.split("\n")[:20]
            files = [f for f in files if f.startswith(SEARCH_ROOT)]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    # ===== RUN SCRIPT =====
    def handle_run(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        path = params.get("path", [""])[0]

        path = urllib.parse.unquote(path)
        path = os.path.expanduser(path)

        # 🔒 allow only ~/.local/bin
        allowed = os.path.expanduser("~/.local/bin")

        if not path.startswith(allowed):
            self.send_response(403)
            self.end_headers()
            return

        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            return

        try:
            subprocess.Popen([path])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


# ===== RUN SERVER =====
if __name__ == "__main__":
    PORT = 8080
    print(f"Running → http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
