"""Data shapes and the deterministic rules that decide when a human must look at a ticket."""
from typing import Literal

from pydantic import BaseModel

URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Extraction(BaseModel):
    category: Literal["billing", "bug", "delivery", "feature_request", "praise", "other"]
    sentiment: Literal["negative", "neutral", "positive"]
    urgency: Literal["low", "medium", "high"]
    summary: str
    refund_requested: bool
    safety_or_legal_risk: bool
    suggested_action: str


class Result(Extraction):
    file: str
    needs_human_review: bool
    review_reason: str = ""


def review_flag(item: Extraction) -> tuple[bool, str]:
    """Rules the model must not decide on its own. Order matters: the first match wins."""
    if item.safety_or_legal_risk:
        return True, "possible safety or legal issue"
    if item.refund_requested:
        return True, "refund needs human approval"
    if item.category == "other":
        return True, "category not recognised"
    return False, ""
