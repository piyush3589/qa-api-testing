"""Tiny offline stand-in for JSONPlaceholder (stdlib only).

Lets the test suite run without internet: `pytest --mock`.
It mimics the subset of JSONPlaceholder behaviour the tests rely on.
"""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def _build_data():
    users = []
    for i in range(1, 11):
        users.append({
            "id": i,
            "name": f"User {i}",
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "address": {
                "street": f"Street {i}",
                "suite": f"Apt. {i}",
                "city": "Mumbai",
                "zipcode": f"4000{i:02d}",
                "geo": {"lat": "19.07", "lng": "72.87"},
            },
            "phone": f"1-770-736-80{i:02d}",
            "website": f"user{i}.example.org",
            "company": {"name": f"Company {i}", "catchPhrase": "Quality first", "bs": "test"},
        })
    posts = [
        {"userId": (i - 1) // 10 + 1, "id": i, "title": f"post title {i}", "body": f"post body {i}"}
        for i in range(1, 101)
    ]
    comments = [
        {
            "postId": (i - 1) // 5 + 1,
            "id": i,
            "name": f"comment {i}",
            "email": f"commenter{i}@example.com",
            "body": f"comment body {i}",
        }
        for i in range(1, 501)
    ]
    return {"users": users, "posts": posts, "comments": comments}


DATA = _build_data()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep test output clean
        pass

    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except ValueError:
            return {}

    def _route(self):
        parsed = urlparse(self.path)
        return parsed.path.rstrip("/"), {k: v[0] for k, v in parse_qs(parsed.query).items()}

    def do_GET(self):
        path, query = self._route()
        m = re.fullmatch(r"/(posts|users|comments)", path)
        if m:
            items = DATA[m.group(1)]
            for key, value in query.items():
                items = [x for x in items if str(x.get(key)) == value]
            return self._send(200, items)
        m = re.fullmatch(r"/(posts|users|comments)/(\d+)", path)
        if m:
            found = [x for x in DATA[m.group(1)] if x["id"] == int(m.group(2))]
            return self._send(200, found[0]) if found else self._send(404, {})
        m = re.fullmatch(r"/posts/(\d+)/comments", path)
        if m:
            return self._send(200, [c for c in DATA["comments"] if c["postId"] == int(m.group(1))])
        self._send(404, {})

    def do_POST(self):
        path, _ = self._route()
        if path in ("/posts", "/comments", "/users"):
            payload = self._read_json()
            payload["id"] = len(DATA[path[1:]]) + 1
            return self._send(201, payload)
        self._send(404, {})

    def _modify(self, merge):
        path, _ = self._route()
        m = re.fullmatch(r"/(posts|users|comments)/(\d+)", path)
        if not m:
            return self._send(404, {})
        found = [x for x in DATA[m.group(1)] if x["id"] == int(m.group(2))]
        if not found:
            return self._send(404, {})
        payload = self._read_json()
        result = {**found[0], **payload} if merge else {**payload}
        result["id"] = int(m.group(2))
        self._send(200, result)

    def do_PUT(self):
        self._modify(merge=False)

    def do_PATCH(self):
        self._modify(merge=True)

    def do_DELETE(self):
        path, _ = self._route()
        if re.fullmatch(r"/(posts|users|comments)/\d+", path):
            return self._send(200, {})
        self._send(404, {})


def start(host="127.0.0.1", port=0):
    """Start the mock in a background thread; returns (server, base_url)."""
    server = ThreadingHTTPServer((host, port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://{host}:{server.server_address[1]}"


if __name__ == "__main__":
    srv, url = start(port=8000)
    print(f"Mock API running at {url} (Ctrl+C to stop)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        srv.shutdown()
