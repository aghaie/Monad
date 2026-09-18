"""Seed the Skill Registry with the skills that exist in code (run once; idempotent)."""
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monad.skills import SkillSpec, SkillRegistry  # noqa: E402

SKILLS = [
    ("claim_classification", "Assign one constitutional origin class to a statement",
     ["statement"], ["origin class"], ["monad.knowledge"], [], ["heuristic; no engine"],
     "tests/test_core.py", "no claim stored without a valid origin", "1.0.0"),
    ("contradiction_detection", "Find stored claims contradicting a new claim",
     ["claim"], ["contradicting claim ids"], ["monad.knowledge"], [],
     ["v1 = same proposition, opposite polarity; misses paraphrase"],
     "tests/test_core.py", "recall on paraphrase pairs (needs engine)", "1.0.0"),
    ("constitutional_check", "Quranic Decision Engine checklist", ["decision"],
     ["VALID|INVALID|UNVERIFIED"], ["monad.core.quran_engine"], [],
     ["principle-level only; answers supplied by caller"], "tests/test_core.py",
     "no INVALID decision executed", "1.0.0"),
    ("candidate_evaluation", "Compare candidate vs baseline metrics", ["metrics", "baseline", "candidate"],
     ["verdict"], ["monad.evaluation"], [], ["needs declared metrics"], "tests/test_core.py",
     "never DEPLOY on critical regression", "1.0.0"),
    ("product_scoring", "Score a problem on 12 discovery dimensions", ["candidate"], ["score"],
     ["monad.factory"], [], ["scores are human/engine supplied"], "tests/test_core.py",
     "ranking stable and validated", "1.0.0"),
    ("skill_creation", "Register, version, activate, roll back skills (meta-skill)",
     ["skill spec"], ["registry record"], ["monad.skills"], [], ["no auto-generation yet"],
     "tests/test_core.py", "rollback restores previous version", "1.0.0"),
    ("web_research", "Ingest and evaluate web sources into the knowledge store",
     ["query"], ["claims with provenance"], ["http", "engine"], ["engine adapter"],
     ["BLOCKED: no engine/API key"], "", "≥1 independent source per stored claim", "0.1.0"),
    ("quranic_reference", "Explainable link from a principle to a Qur'anic basis",
     ["principle"], ["reference + explanation"], ["engine"], ["engine adapter"],
     ["must be explainable; never forced onto technical decisions"], "",
     "every reference has an explanation reviewed by a human", "0.1.0"),
    # v0.2 — reading skills (اقرأ): engine-free, stdlib only
    ("web_research", "Read a web source and store what it said as a DATA claim with provenance (url, sha256, time)",
     ["url"], ["DATA claim with provenance"], ["urllib", "html.parser", "monad.knowledge"], [],
     ["records what a source said, not whether it is true; no search/query — URL must be given; no JS rendering"],
     "tests/test_read.py", "every stored claim has url + sha256; staleness 30 days", "0.2.0"),
    ("quranic_reference", "Verse-level citable reference: lookup sura:ayah or search a term → REVELATION claims",
     ["sura:ayah | term"], ["REVELATION claims with provenance"], ["monad.quran", "data/quran/quran-simple.csv"], [],
     ["lookup/search only; explaining a principle→verse link stays human/engine work; never forced onto technical decisions"],
     "tests/test_read.py", "every returned verse cites tanzil:quran-simple#sura:ayah exactly", "0.2.0"),
]

reg = SkillRegistry(ROOT / "data" / "skills.jsonl")
passed = subprocess.run([sys.executable, "-m", "pytest", "-q", ],
                        cwd=ROOT, capture_output=True).returncode == 0
for name, purpose, i, o, t, d, lim, tests, ev, ver in SKILLS:
    if reg.get(name, ver):
        continue
    reg.register(SkillSpec(name, purpose, i, o, t, d, lim, tests, ev, ver),
                 why="genesis capability", expected_benefit="constitutional operation from day one")
    reg.activate(name, ver, test_passed=passed and bool(tests))
for n in reg.names():
    c = reg.current(n)
    print(f"{n:26s} {c.version:7s} {c.status}")
