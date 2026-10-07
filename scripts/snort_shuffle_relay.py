from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os
import datetime
import json

TARGET = os.environ["SHUFFLE_WEBHOOK_URL"]
LOG = os.environ.get("RELAY_LOG", "relay.log")


def log(line):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{now} {line}\n")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        try:
            json.loads(body.decode("utf-8"))
            req = Request(TARGET, data=body, method="POST", headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=120) as resp:
                response = resp.read()
                status = resp.status
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)
            log(f"forwarded status={status} body={body.decode('utf-8', errors='replace')} response={response.decode('utf-8', errors='replace')}")
        except (HTTPError, URLError, Exception) as exc:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = json.dumps({"success": False, "error": str(exc)}).encode("utf-8")
            self.wfile.write(data)
            log(f"failed error={exc} body={body.decode('utf-8', errors='replace')}")

    def log_message(self, fmt, *args):
        log(fmt % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer((os.environ.get("RELAY_BIND", "127.0.0.1"), int(os.environ.get("RELAY_PORT", "8088"))), Handler)
    log("relay started on 0.0.0.0:8088")
    server.serve_forever()
