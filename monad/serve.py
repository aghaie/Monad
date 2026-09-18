"""`monad serve` — Mizan on localhost with zero-step usage sync. Stdlib only, no dependencies.

GET  /            → products/mizan/index.html (and any file in that folder)
POST /sync        → body = Mizan's full claim list (JSON array); snapshot to data/usage/mizan.jsonl,
                    ingest into the knowledge store (idempotent), reply with usage numbers.
Opened as file:// Mizan still works; only the sync is skipped (export + `monad ingest` remain).
"""
from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from monad.knowledge import KnowledgeStore
from monad.usage import ingest, usage


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, root: Path, **kw):
        self.root = root
        super().__init__(*a, directory=str(root / "products" / "mizan"), **kw)

    def do_POST(self):
        if self.path != "/sync":
            return self.send_error(404)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            rows = json.loads(body)
            assert isinstance(rows, list)
        except Exception:
            return self.send_error(400, "expected a JSON array of claims")
        snap = self.root / "data" / "usage" / "mizan.jsonl"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        store = KnowledgeStore(self.root / "data" / "knowledge.jsonl")
        new = ingest(store, snap)
        out = json.dumps({"ingested": new, **usage(store)}, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, fmt, *args):  # one quiet line per request
        print(f"  {self.command} {self.path} {args[1] if len(args) > 1 else ''}")


def make_server(root: Path, port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, root=root))


def serve(root: Path, port: int = 8765) -> None:
    srv = make_server(root, port)
    print(f"Mizan: http://127.0.0.1:{srv.server_port}/  (Ctrl+C to stop; every change syncs into data/)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
