"""Engine adapters. MONAD's identity is never a model; models are replaceable engines.

Selection: MONAD_ENGINE env var (auto | null | lmstudio). Adding a provider = one class
implementing `complete` and one REGISTRY line.
"""
from __future__ import annotations

import json
import os
import urllib.request
from abc import ABC, abstractmethod


class Engine(ABC):
    name: str = "abstract"

    @abstractmethod
    def complete(self, prompt: str, *, system: str = "") -> str: ...


class NullEngine(Engine):
    """Returns an honest 'I don't know'. Keeps the loop runnable without any provider."""
    name = "null"

    def complete(self, prompt: str, *, system: str = "") -> str:
        return "UNKNOWN: no reasoning engine configured"


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


REGISTRY: dict[str, type[Engine]] = {"null": NullEngine, "lmstudio": LMStudioEngine}


def get_engine(name: str | None = None) -> Engine:
    """MONAD_ENGINE = null | lmstudio | auto (default: auto = lmstudio if its server answers, else null)."""
    name = name or os.environ.get("MONAD_ENGINE", "auto")
    if name == "auto":
        try:
            urllib.request.urlopen(LMStudioEngine().url + "/models", timeout=2).close()
            name = "lmstudio"
        except Exception:
            name = "null"
    return REGISTRY[name]()
