"""Product Discovery — iteration 001.

Scores (1..5) are ENGINEERING_DECISION by the builder, not measured data. They are
recorded so a later iteration with real usage data can refute them.
Constraints observed: no host, no engine key, no real users yet → the first product
must run anywhere (single file), need no server, and be useful to the founder today.
"""
from pathlib import Path
import sys, json
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monad.factory import ProblemCandidate, Product, SoftwareFactory, rank  # noqa: E402
from monad.knowledge import Claim, KnowledgeStore  # noqa: E402
from monad.core.quran_engine import Decision, check  # noqa: E402

S = lambda **k: k  # noqa: E731
cands = [
    ProblemCandidate("Mizan — claim & evidence ledger (offline, Persian/English)",
        "People (starting with the founder) mix claim, evidence, opinion and hypothesis; "
        "no light tool separates them with provenance, confidence and contradictions.",
        S(human_need=4, truth=5, utility=4, impact=3, feasibility=5, cost=1, risk=1, reach=3,
          urgency=3, existing_solutions=2, existing_failures=4, potential_improvement=4),
        evidence=["MONAD_CONSTITUTION.md Article 5", "builder observation: no Persian tool found (UNVERIFIED — no web research skill in runtime)"]),
    ProblemCandidate("Persian text normalizer",
        "Normalize Persian text (ي/ی, ك/ک, ZWNJ).",
        S(human_need=3, truth=2, utility=3, impact=2, feasibility=5, cost=1, risk=1, reach=3,
          urgency=1, existing_solutions=5, existing_failures=2, potential_improvement=2),
        evidence=["hazm, parsivar exist (builder knowledge, DATA-stale)"]),
    ProblemCandidate("Telegram truth-check bot",
        "Bot that logs claims and asks for evidence in chat.",
        S(human_need=4, truth=4, utility=4, impact=3, feasibility=2, cost=2, risk=2, reach=4,
          urgency=2, existing_solutions=2, existing_failures=3, potential_improvement=4),
        evidence=["BLOCKED: needs bot token + host"]),
    ProblemCandidate("Source-reliability evaluator",
        "Score web sources for reliability.",
        S(human_need=4, truth=5, utility=4, impact=4, feasibility=1, cost=3, risk=3, reach=3,
          urgency=3, existing_solutions=3, existing_failures=4, potential_improvement=4),
        evidence=["BLOCKED: needs reasoning engine"]),
]
ranked = rank(cands)
for score, c in ranked:
    print(f"{score:4.2f}  {c.title}")
best = ranked[0][1]

ks = KnowledgeStore(ROOT / "data" / "knowledge.jsonl")
for score, c in ranked:
    ks.add(Claim(text=f"discovery-001 score {score} for '{c.title}'", origin="ENGINEERING_DECISION",
                 confidence=0.4, source="scripts/discover_product_001.py", evidence=[], tags=["discovery"],
                 expires_days=90))
ks.add(Claim(text="Mizan is useful to real users", origin="HYPOTHESIS", confidence=0.4,
             source="scripts/discover_product_001.py", tags=["product:mizan"]))

d = Decision("build Mizan", "offline single-file claim ledger", {
    "truth_over_falsehood": True, "justice_no_oppression": True, "no_corruption": True,
    "no_deception": True, "trust_and_covenant": True, "no_waste": True,
    "knowledge_over_conjecture": True, "human_dignity": True, "reform_not_appearance": True,
    "better_purer_path": True})
verdict = check(d)
print("constitutional check:", verdict.result)
assert verdict.result == "VALID"

sf = SoftwareFactory(ROOT / "data" / "products.jsonl")
p = Product(
    name="mizan",
    why="Article 5: data, analysis, hypothesis and conclusion must be kept separate — for humans too.",
    who="Truth-seeking individuals; first user: Ali Aghaei.",
    problem=best.description,
    solution="Single-file offline web app (Persian RTL + English): log claims with one of nine origin "
             "classes, confidence, source, evidence links, contradiction flags; export/import JSON "
             "compatible with MONAD's knowledge store.",
    measurement="Real use: number of claims logged per week by real users; share of claims with a "
                "source; number of contradictions surfaced. Success threshold set AFTER first 30 days of data (no invented target).",
)
p.advance("REQUIREMENTS", "derived from Constitution + founder profile")
p.advance("RESEARCH", "UNVERIFIED: existing-tool survey needs web_research skill")
p.advance("ARCHITECTURE", "static HTML, no backend, JSON export == knowledge store schema")
sf.save(p)
print(json.dumps({"product": p.name, "stage": p.stage}, ensure_ascii=False))
