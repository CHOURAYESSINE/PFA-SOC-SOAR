import importlib.util
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]

class RepositoryTests(unittest.TestCase):
    def test_json_files(self):
        for path in ROOT.rglob("*.json"):
            with self.subTest(file=str(path.relative_to(ROOT))):
                json.loads(path.read_text(encoding="utf-8-sig"))

    def test_workflow_graph(self):
        workflow = json.loads((ROOT / "shuffle/workflow.template.json").read_text(encoding="utf-8-sig"))
        ids = [a["id"] for a in workflow["actions"]] + [t["id"] for t in workflow["triggers"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn(workflow["start"], ids)
        for branch in workflow["branches"]:
            self.assertIn(branch["source_id"], ids)
            self.assertIn(branch["destination_id"], ids)

    def test_relay_forward_and_invalid_json(self):
        received = []
        class Sink(BaseHTTPRequestHandler):
            def do_POST(self):
                received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"success":true}')
            def log_message(self, *args):
                pass
        sink = ThreadingHTTPServer(("127.0.0.1", 0), Sink)
        threading.Thread(target=sink.serve_forever, daemon=True).start()
        with tempfile.TemporaryDirectory() as temp:
            os.environ["SHUFFLE_WEBHOOK_URL"] = f"http://127.0.0.1:{sink.server_port}/"
            os.environ["RELAY_LOG"] = str(Path(temp) / "relay.log")
            spec = importlib.util.spec_from_file_location("relay", ROOT / "scripts/snort_shuffle_relay.py")
            relay = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(relay)
            server = ThreadingHTTPServer(("127.0.0.1", 0), relay.Handler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                payload = {"attacker_ip": "203.0.113.10", "sid": "1001", "alert": "test"}
                request = Request(f"http://127.0.0.1:{server.server_port}/", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
                with urlopen(request, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(json.load(response)["success"])
                self.assertEqual(received, [payload])
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(f"http://127.0.0.1:{server.server_port}/", data=b'not-json'), timeout=5)
                self.assertEqual(error.exception.code, 502)
                self.assertEqual(received, [payload])
            finally:
                server.shutdown()
                server.server_close()
        sink.shutdown()
        sink.server_close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
