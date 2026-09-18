"""Engine adapters. MONAD's identity is never a model; models are replaceable engines.

Only the interface and a NullEngine exist now (no API keys in this environment —
recorded as BLOCKED). Adding a provider = one class implementing `complete`.
"""
from __future__ import annotations

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


REGISTRY: dict[str, type[Engine]] = {"null": NullEngine}


def get_engine(name: str = "null") -> Engine:
    return REGISTRY[name]()
