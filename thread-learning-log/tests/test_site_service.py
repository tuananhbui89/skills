import importlib.util
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

class ServiceTests(unittest.TestCase):
    def test_health_reuses_only_identified_site_and_detects_wrong_server(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/site_service.py'
        self.assertTrue(path.exists(), 'Persistent site launcher must exist')
        spec = importlib.util.spec_from_file_location('site_service', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = {'appId': 'personal-learning-log', 'weeks': {'2026-11-16': {'tasks': []}}}
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            def log_message(self, *args): pass
        with HTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f'http://127.0.0.1:{server.server_port}'
            try:
                self.assertEqual(module.health(url)['appId'], 'personal-learning-log')
                data['appId'] = 'unrelated'
                with self.assertRaisesRegex(RuntimeError, 'another service'):
                    module.health(url)
            finally:
                server.shutdown()

if __name__ == '__main__': unittest.main()
