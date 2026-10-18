"""Serve the static frontend locally with public API configuration from .env."""

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


FRONTEND_DIR = Path(__file__).resolve().parent


def api_base_url():
    env_file = FRONTEND_DIR / ".env"
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() != "API_BASE_URL":
            continue
        value = value.strip().strip('"\'')
        parsed = urlsplit(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("API_BASE_URL must be an HTTP(S) URL without credentials, query, or fragment")
        parsed.port  # Validate a supplied port.
        return value
    raise ValueError("API_BASE_URL is missing from frontend/.env")


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _serve(self, head_only=False):
        path = unquote(urlsplit(self.path).path)
        if path == "/config.txt":
            try:
                body = f"API_BASE_URL={api_base_url()}\n".encode("utf-8")
            except (OSError, ValueError):
                self.send_error(500, "Frontend API configuration is invalid")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return
        if any(part.startswith(".") for part in path.replace("\\", "/").split("/") if part):
            self.send_error(404)
            return
        if head_only:
            super().do_HEAD()
        else:
            super().do_GET()

    def do_GET(self):
        self._serve()

    def do_HEAD(self):
        self._serve(head_only=True)

    def list_directory(self, path):
        self.send_error(404)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve the Kubernetes monitoring frontend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5500)
    args = parser.parse_args()
    ThreadingHTTPServer((args.host, args.port), FrontendHandler).serve_forever()
