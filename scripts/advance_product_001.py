"""Advance Mizan through the pipeline based on what actually happened (not claimed)."""
from pathlib import Path
import sys, subprocess
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monad.factory import SoftwareFactory  # noqa: E402

sf = SoftwareFactory(ROOT / "data" / "products.jsonl")
p = next(x for x in sf.products() if x.name == "mizan")
tests_ok = subprocess.run([sys.executable, "-m", "pytest", "-q", "products/mizan"], cwd=ROOT,
                          capture_output=True).returncode == 0
p.advance("PROTOTYPE", "single-file HTML built")
p.advance("IMPLEMENTATION", "provenance rule, contradiction detection, export/import, filters")
p.advance("TEST", f"3 browser tests (Playwright/Chromium): {'PASS' if tests_ok else 'FAIL'}", blocked=not tests_ok)
p.advance("SECURITY_REVIEW", "no network, no backend, data stays in the user's browser; HTML-escaped rendering; import trusts local file (acceptable for v0.1)")
p.advance("USER_EXPERIENCE", "Persian RTL + English labels; not yet reviewed by a real user (UNKNOWN)")
p.advance("DEPLOYMENT", "BLOCKED: no host. Delivered as a file to Ali; runs by opening it.", blocked=True)
sf.save(p)
print(p.name, p.stage, [h["to"] for h in p.history])
