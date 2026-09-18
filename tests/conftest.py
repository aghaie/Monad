import os, pytest


@pytest.fixture(autouse=True)
def _no_live_engine(monkeypatch):
    """Tests never call a real model unless they opt in (Article 7: no hidden dependencies)."""
    monkeypatch.setenv("MONAD_ENGINE", os.environ.get("MONAD_TEST_ENGINE", "null"))
