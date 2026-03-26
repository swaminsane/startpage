#!/usr/bin/env python3

import http.server
import socketserver
import subprocess
import json
import urllib.parse
import os
import re

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # ===== FILE SEARCH =====
        if self.path.startswith("/search"):
            self.handle_search()
            return

        # ===== MPD INFO =====
        if self.path.startswith("/mpd"):
            self.handle_mpd()
            return

        # ===== MPD TOGGLE =====
        if self.path.startswith("/mpd-toggle"):
            subprocess.run(["/usr/bin/mpc", "toggle"])
            self.send_response(200)
            self.end_headers()
            return

        # ===== DEFAULT (serve files) =====
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # ===== FILE SEARCH =====
    def handle_search(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        q = params.get("q", [""])[0]

        try:
            result = subprocess.run(
                ["find", os.path.expanduser("~"), "-iname", f"*{q}*"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            files = result.stdout.strip().split("\n")[:20] if result.stdout else []

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    # ===== MPD WITH ROBUST PROGRESS =====
    def handle_mpd(self):
        try:
            output = subprocess.run(
                ["/usr/bin/mpc"],
                stdout=subprocess.PIPE,
                text=True
            ).stdout.strip().split("\n")

            if len(output) < 2:
                data = {
                    "song": "Nothing playing",
                    "progress": 0
                }
            else:
                song = output[0]
                status_line = output[1]

                # Extract percentage safely using regex
                match = re.search(r"\((\d+)%\)", status_line)

                if match:
                    progress = int(match.group(1))
                else:
                    progress = 0

                data = {
                    "song": song,
                    "progress": progress
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        except Exception as e:
            print("MPD ERROR:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


# ===== START SERVER =====
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
