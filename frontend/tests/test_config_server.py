"""Isolated checks for the local frontend config endpoint."""

import importlib.util
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


SERVER_PATH = Path(__file__).resolve().parents[1] / "serve.py"
SPEC = importlib.util.spec_from_file_location("frontend_serve", SERVER_PATH)
serve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve)


class ConfigServerTests(unittest.TestCase):
    def test_config_changes_and_env_is_private(self):
        with tempfile.TemporaryDirectory() as directory:
            serve.FRONTEND_DIR = Path(directory)
            env_file = serve.FRONTEND_DIR / ".env"
            env_file.write_text("API_BASE_URL=http://127.0.0.1:8000\n", encoding="utf-8")
            server = ThreadingHTTPServer(("127.0.0.1", 0), serve.FrontendHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with urlopen(f"{base}/config.txt") as response:
                    self.assertEqual(response.read().decode(), "API_BASE_URL=http://127.0.0.1:8000\n")
                    self.assertEqual(response.headers["Cache-Control"], "no-store")

                env_file.write_text("API_BASE_URL=https://backend.example:8443\n", encoding="utf-8")
                with urlopen(f"{base}/config.txt") as response:
                    self.assertEqual(response.read().decode(), "API_BASE_URL=https://backend.example:8443\n")

                with self.assertRaises(HTTPError) as hidden:
                    urlopen(f"{base}/.env")
                self.assertEqual(hidden.exception.code, 404)

                env_file.write_text("API_BASE_URL=invalid\n", encoding="utf-8")
                with self.assertRaises(HTTPError) as invalid:
                    urlopen(f"{base}/config.txt")
                self.assertEqual(invalid.exception.code, 500)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == "__main__":
    unittest.main()
