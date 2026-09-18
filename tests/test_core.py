import pytest

from monad.knowledge import Claim, KnowledgeStore
from monad.skills import SkillSpec, SkillRegistry
from monad.agents import AgentSpec, AgentFactory
from monad.factory import Product, ProblemCandidate, SoftwareFactory, rank, DIMENSIONS
from monad.evaluation import Metric, evaluate
from monad.core.quran_engine import Decision, check
from monad.core.loop import MonadLoop


# ---- Knowledge Engine ------------------------------------------------------
def test_claim_requires_origin_and_source():
    with pytest.raises(ValueError):
        Claim(text="x", origin="TRUTH", source="s")
    with pytest.raises(ValueError):
        Claim(text="x", origin="DATA")  # no provenance
    Claim(text="?", origin="UNKNOWN")  # 'I don't know' needs no source


def test_contradictions_are_recorded_not_hidden(tmp_path):
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    a = ks.add(Claim(text="The tool is useful", origin="HYPOTHESIS", source="ali"))
    b = ks.add(Claim(text="The tool is not useful", origin="EMPIRICAL_RESULT", source="survey-1"))
    pairs = ks.contradictions()
    assert len(pairs) == 1
    assert {pairs[0][0].id, pairs[0][1].id} == {a.id, b.id}
    assert b.id in ks.get(a.id).contradicts


def test_dependent_evidence_counts_once(tmp_path):
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    e1 = ks.add(Claim(text="report says X", origin="DATA", source="report-A"))
    e2 = ks.add(Claim(text="blog quoting report says X", origin="DATA", source="report-A"))
    e3 = ks.add(Claim(text="independent measurement X", origin="DATA", source="lab-B"))
    h = ks.add(Claim(text="X holds", origin="HYPOTHESIS", source="monad", evidence=[e1.id, e2.id, e3.id]))
    assert ks.independent_evidence_count(h.id) == 2


def test_staleness(tmp_path):
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    c = Claim(text="price is 5", origin="DATA", source="site", expires_days=1,
              created="2020-01-01T00:00:00+00:00")
    ks.add(c)
    assert ks.stale() and ks.stale()[0].id == c.id


# ---- Skill Factory ---------------------------------------------------------
def _spec(v="1.0.0", tests="tests/test_core.py"):
    return SkillSpec(name="demo", purpose="p", inputs=["a"], outputs=["b"], tools=["t"],
                     dependencies=["d"], limitations=["l"], tests=tests, evaluation="acc>0.9",
                     version=v)


def test_skill_activation_requires_tests(tmp_path):
    reg = SkillRegistry(tmp_path / "s.jsonl")
    reg.register(_spec(tests=""), why="w", expected_benefit="b")
    assert reg.activate("demo", "1.0.0", test_passed=True).status == "SPEC"
    reg.register(_spec(v="1.1.0"), why="w", expected_benefit="b")
    assert reg.activate("demo", "1.1.0", test_passed=False).status == "SPEC"
    assert reg.activate("demo", "1.1.0", test_passed=True).status == "ACTIVE"


def test_skill_rollback(tmp_path):
    reg = SkillRegistry(tmp_path / "s.jsonl")
    reg.register(_spec("1.0.0"), "w", "b"); reg.activate("demo", "1.0.0", True)
    reg.register(_spec("1.1.0"), "w", "b"); reg.activate("demo", "1.1.0", True)
    prev = reg.rollback("demo", reason="worse on eval")
    assert prev.version == "1.0.0"
    assert reg.current("demo").version == "1.0.0"
    assert reg.gaps(["demo", "missing"]) == ["missing"]


# ---- Agent Factory ---------------------------------------------------------
def test_agent_needs_reason_tests_and_retirement(tmp_path):
    reg = SkillRegistry(tmp_path / "s.jsonl")
    reg.register(_spec(), "w", "b"); reg.activate("demo", "1.0.0", True)
    af = AgentFactory(tmp_path / "a.jsonl", reg)
    with pytest.raises(ValueError):
        af.create(AgentSpec("x", "p", ["demo"], why_needed="", test_plan="t", retire_when="r"))
    a = af.create(AgentSpec("x", "p", ["demo"], why_needed="y", test_plan="t", retire_when="r"))
    assert a.status == "ACTIVE"
    with pytest.raises(ValueError):  # duplicate skill set
        af.create(AgentSpec("x2", "p", ["demo"], why_needed="y", test_plan="t", retire_when="r"))
    b = af.create(AgentSpec("z", "p", ["demo", "nope"], why_needed="y", test_plan="t", retire_when="r"))
    assert b.status == "PROPOSED"  # missing skill → not active


# ---- Software Factory / Product Discovery ----------------------------------
def test_product_discovery_ranking_and_pipeline(tmp_path):
    good = ProblemCandidate("A", "d", {d: 5 for d in DIMENSIONS} | {"cost": 1, "risk": 1, "existing_solutions": 1})
    bad = ProblemCandidate("B", "d", {d: 1 for d in DIMENSIONS} | {"cost": 5, "risk": 5, "existing_solutions": 5})
    ranked = rank([bad, good])
    assert ranked[0][1].title == "A" and ranked[0][0] == 5.0 and ranked[1][0] == 1.0
    sf = SoftwareFactory(tmp_path / "p.jsonl")
    with pytest.raises(ValueError):
        sf.save(Product("p", why="", who="w", problem="p", solution="s", measurement="m"))
    p = Product("p", "why", "who", "prob", "sol", "meas")
    p.advance("REQUIREMENTS", "ok"); p.advance("DEPLOYMENT", "no host", blocked=True)
    assert p.stage == "REQUIREMENTS" and p.history[-1]["blocked"]
    with pytest.raises(ValueError):
        p.advance("PROBLEM", "backwards")
    p.record_outcome(False, "nobody used it")
    sf.save(p)
    assert sf.products()[0].outcome == "NOT_USEFUL"


# ---- Evaluation Engine -----------------------------------------------------
def test_evaluate_verdicts():
    m = [Metric("accuracy"), Metric("latency_ms", higher_is_better=False, critical=True)]
    assert evaluate(m, {"accuracy": .8, "latency_ms": 100}, {"accuracy": .9, "latency_ms": 90}).decision == "DEPLOY"
    assert evaluate(m, {"accuracy": .8, "latency_ms": 100}, {"accuracy": .9, "latency_ms": 200}).decision == "ROLLBACK"
    assert evaluate(m, {"accuracy": .8, "latency_ms": 100}, {"accuracy": .7, "latency_ms": 100}).decision == "ROLLBACK"
    assert evaluate(m, {}, {"accuracy": .9}).decision == "INCONCLUSIVE"
    assert evaluate(m, {"accuracy": .8, "latency_ms": 100}, {"accuracy": .8, "latency_ms": 100}).decision == "INCONCLUSIVE"


# ---- Quranic Decision Engine ----------------------------------------------
def test_constitutional_check():
    ok = {k: True for k in ("truth_over_falsehood", "justice_no_oppression", "no_corruption",
                            "no_deception", "trust_and_covenant", "no_waste",
                            "knowledge_over_conjecture", "human_dignity",
                            "reform_not_appearance", "better_purer_path")}
    assert check(Decision("d", "x", ok)).result == "VALID"
    assert check(Decision("d", "x", ok | {"no_deception": False})).result == "INVALID"
    assert check(Decision("d", "x", ok | {"no_waste": None})).result == "UNVERIFIED"
    assert check(Decision("d", "x", {}, is_significant=False)).result == "VALID"


# ---- Core loop -------------------------------------------------------------
def test_loop_iterates_and_persists(tmp_path):
    loop = MonadLoop(tmp_path)
    r1 = loop.iterate()
    r2 = MonadLoop(tmp_path).iterate()
    assert (r1.number, r2.number) == (1, 2)
    assert "no reasoning engine" in r2.blocked[0]
    assert r2.observations["claims"] == 1  # r1's self-observation was learned
    assert (tmp_path / "reports" / "iteration_002.json").exists()


def test_persian_contradiction(tmp_path):
    ks = KnowledgeStore(tmp_path / "k.jsonl")
    ks.add(Claim(text="این ابزار مفید است", origin="HYPOTHESIS", source="علی"))
    ks.add(Claim(text="این ابزار مفید نیست", origin="EMPIRICAL_RESULT", source="نظرسنجی"))
    assert len(ks.contradictions()) == 1
