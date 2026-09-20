"""Engine adapters. MONAD's identity is never a model; models are replaceable engines.

Selection: MONAD_ENGINE env var (auto | null | session | lmstudio). Adding a provider = one
class implementing `complete` and one REGISTRY line.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path


class Engine(ABC):
    name: str = "abstract"

    @abstractmethod
    def complete(self, prompt: str, *, system: str = "") -> str: ...

    def pending(self) -> list[dict]:
        """Questions this engine has asked and nobody has answered yet."""
        return []


class NullEngine(Engine):
    """Returns an honest 'I don't know'. Keeps the loop runnable without any provider."""
    name = "null"

    def complete(self, prompt: str, *, system: str = "") -> str:
        return "UNKNOWN: no reasoning engine configured"


class Pending(Exception):
    """The session engine has recorded the question but has no answer yet (Article 16)."""

    def __init__(self, qid: str, path: Path):
        self.id, self.path = qid, path
        super().__init__(f'pending {qid}: answer it with `python3 -m monad answer {qid} "<answer>"`')


QA_PATH = Path(__file__).resolve().parents[2] / "data" / "engine_qa.jsonl"


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def answer(path: Path, qid: str, text: str) -> None:
    """Record an answer. Append-only: the last answer for an id wins, earlier ones stay in history."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": qid, "answered": datetime.now(timezone.utc).isoformat(),
                            "answer": text}, ensure_ascii=False) + "\n")


class SessionEngine(Engine):
    """The agent or human at this terminal is the reasoning engine — no provider, no API key.

    A question is looked up in `data/engine_qa.jsonl` by the hash of (system, prompt). Known →
    its answer, forever and offline. Unknown → the question is appended as pending and `Pending`
    is raised; the caller records that as BLOCKED instead of inventing an answer.
    """
    name = "session"

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or os.environ.get("MONAD_QA") or QA_PATH)

    def complete(self, prompt: str, *, system: str = "") -> str:
        qid = hashlib.sha256(f"{system}\n{prompt}".encode()).hexdigest()[:12]
        rows = _rows(self.path)
        for r in reversed(rows):
            if r["id"] == qid and r.get("answer") is not None:
                return r["answer"]
        if not any(r["id"] == qid for r in rows):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": qid, "asked": datetime.now(timezone.utc).isoformat(),
                                    "system": system, "prompt": prompt, "answer": None},
                                   ensure_ascii=False) + "\n")
        raise Pending(qid, self.path)

    def pending(self) -> list[dict]:
        rows = _rows(self.path)
        answered = {r["id"] for r in rows if r.get("answer") is not None}
        return [r for r in rows if r.get("prompt") is not None and r["id"] not in answered]


class LMStudioEngine(Engine):
    """Local LM Studio server (OpenAI-compatible /v1/chat/completions). Stdlib only."""
    name = "lmstudio"

    def __init__(self, url: str | None = None, model: str | None = None):
        self.url = (url or os.environ.get("MONAD_ENGINE_URL", "http://localhost:1234/v1")).rstrip("/")
        self.model = model or os.environ.get("MONAD_ENGINE_MODEL", "google/gemma-4-26b-a4b-qat")

    def complete(self, prompt: str, *, system: str = "") -> str:
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0}).encode()
        req = urllib.request.Request(f"{self.url}/chat/completions", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:  # local; large models are slow
            return json.load(r)["choices"][0]["message"]["content"]


REGISTRY: dict[str, type[Engine]] = {"null": NullEngine, "session": SessionEngine,
                                     "lmstudio": LMStudioEngine}


def get_engine(name: str | None = None) -> Engine:
    """MONAD_ENGINE = null | session | lmstudio | auto.

    auto = lmstudio if its server answers, else session: the terminal itself can reason, and
    when it cannot it says so — strictly more than NullEngine, and depends on no provider.
    """
    name = name or os.environ.get("MONAD_ENGINE", "auto")
    if name == "auto":
        try:
            urllib.request.urlopen(LMStudioEngine().url + "/models", timeout=2).close()
            name = "lmstudio"
        except Exception:
            name = "session"
    return REGISTRY[name]()
