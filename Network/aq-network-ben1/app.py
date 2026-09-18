#!/usr/bin/env python3
"""AcmeCache -- a multi-service box for a network-recon challenge.

Two services run in one container:
  * :8000  a small HTTP admin page that hints the backing store is on :6379.
  * :6379  a Redis-like TCP service with NO authentication. Any client that
           connects and sends a command (INFO / KEYS / GET flag) is handed the
           flag -- standing in for an internet-exposed, unauthenticated Redis.

The intended path: port-scan the box, find the open data service, connect
(redis-cli or netcat), and read the flag.
"""
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = "f13{exposed_redis_no_auth}"


class Recon(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>AcmeCache Admin</h1>"
                         b"<p>Backing store: redis on port 6379 "
                         b"(internal use only).</p>")

    def log_message(self, *a):
        pass


def http_service():
    HTTPServer(("0.0.0.0", 8000), Recon).serve_forever()


def handle(conn):
    try:
        conn.sendall(b"# AcmeCache. No auth required. Try INFO or KEYS.\r\n")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            cmd = data.decode(errors="ignore").upper()
            if "INFO" in cmd or "KEYS" in cmd or "GET FLAG" in cmd:
                conn.sendall(f"flag:{FLAG}\r\n".encode())
            else:
                conn.sendall(b"+OK\r\n")
    except OSError:
        pass
    finally:
        conn.close()


def data_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 6379))
    s.listen(16)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    threading.Thread(target=http_service, daemon=True).start()
    data_service()
