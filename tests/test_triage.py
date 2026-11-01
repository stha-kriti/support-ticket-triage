import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import triage
from schema import Extraction, review_flag

GOOD = {"category": "delivery", "sentiment": "negative", "urgency": "high", "summary": "s",
        "refund_requested": False, "safety_or_legal_risk": False, "suggested_action": "check courier"}


def fake_client(*replies):
    it = iter(replies)
    create = lambda **kw: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=next(it)))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def test_retry_recovers_from_invalid_schema():
    bad = json.dumps({**GOOD, "urgency": "URGENT!!"})
    item = triage.extract(fake_client(bad, json.dumps(GOOD)), "m", "text")
    assert item.urgency == "high"


def test_review_rules():
    base = Extraction(**GOOD)
    assert review_flag(base) == (False, "")
    assert review_flag(base.model_copy(update={"refund_requested": True}))[1] == "refund needs human approval"
    assert review_flag(base.model_copy(update={"category": "other"}))[0]


def test_safety_risk_wins_over_other_rules():
    risky = Extraction(**{**GOOD, "refund_requested": True, "safety_or_legal_risk": True})
    assert review_flag(risky)[1] == "possible safety or legal issue"


def test_process_survives_total_failure(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    results = triage.process(tmp_path, fake_client("not json", "still not json"), "m")
    assert results[0].needs_human_review and results[0].urgency == "high"


def test_human_review_tickets_sorted_first(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    calm_high = json.dumps(GOOD)
    refund_low = json.dumps({**GOOD, "urgency": "low", "refund_requested": True})
    results = triage.process(tmp_path, fake_client(calm_high, refund_low), "m")
    assert [r.file for r in results] == ["b.txt", "a.txt"]
