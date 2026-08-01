#!/usr/bin/env python3
"""PhotoPrivacy server — serves static files + feedback API"""
import http.server
import json
import os
import socketserver
from datetime import datetime
from urllib.parse import parse_qs

PORT = int(os.environ.get("PORT", 3000))
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "feedback.json")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/feedback":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            email = data.get("email", "").strip()
            message = data.get("message", "").strip()
            if not message:
                self.send_error(400, "Message required")
                return

            entry = {
                "email": email,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            # Load existing feedback
            feedbacks = []
            if os.path.exists(FEEDBACK_FILE):
                try:
                    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                        feedbacks = json.load(f)
                except (json.JSONDecodeError, IOError):
                    feedbacks = []

            feedbacks.append(entry)

            with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/api/feedback":
            feedbacks = []
            if os.path.exists(FEEDBACK_FILE):
                try:
                    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                        feedbacks = json.load(f)
                except (json.JSONDecodeError, IOError):
                    feedbacks = []

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(feedbacks, ensure_ascii=False, indent=2).encode())
        else:
            super().do_GET()


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"PhotoPrivacy server running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
