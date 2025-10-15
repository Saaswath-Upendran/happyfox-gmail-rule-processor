from __future__ import annotations
import logging, datetime
from dataclasses import dataclass
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


@dataclass
class Condition:
    field: str
    predicate: str
    value: Any


@dataclass
class Rule:
    name: str
    conditions: List[Condition]
    actions: List[Dict[str, Any]]


@dataclass
class RuleSet:
    collection_predicate: str # "All" | "Any"
    rules: List[Rule]


# ---- Evaluation helpers ----


def _match_string(value: str, predicate: str, expected: str) -> bool:
    v = value or ""
    e = expected or ""
    if predicate == "Contains":
        return e.lower() in v.lower()
    elif predicate == "DoesNotContain":
        return e.lower() not in v.lower()
    elif predicate == "Equals":
        return v.lower() == e.lower()
    elif predicate == "DoesNotEqual":
        return v.lower() != e.lower()
    else:
        raise ValueError(f"Unsupported string predicate: {predicate}")





def _match_date(dt: datetime.datetime | None, predicate: str, n: int) -> bool:
    if not dt:
        return False
    now = datetime.datetime.now(datetime.timezone.utc)
    if predicate == "LessThanDays":
        return (now - dt).days < n
    if predicate == "GreaterThanDays":
        return (now - dt).days > n
    if predicate == "LessThanMonths":
        return (now - dt).days < n * 30
    if predicate == "GreaterThanMonths":
        return (now - dt).days > n * 30
    raise ValueError(f"Unsupported date predicate: {predicate}")




def evaluate_rule(email_row: Any, rule: Rule) -> bool:
    results: List[bool] = []
    for c in rule.conditions:
        field = c.field
        if field in ("From", "Subject", "Message"):
            val = getattr(email_row, "from_addr" if field == "From" else ("subject" if field == "Subject" else "snippet"), "")
            results.append(_match_string(val, c.predicate, str(c.value)))
        elif field == "ReceivedAt":
            results.append(_match_date(getattr(email_row, "received_at", None), c.predicate, int(c.value)))
        else:
            raise ValueError(f"Unsupported field: {field}")
# For a single rule, all its conditions must match to apply that rule's actions
    return all(results)

def compile_ruleset(data: Dict[str, Any]) -> RuleSet:
    rs = RuleSet(
    collection_predicate=data.get("collection_predicate", "All"),
    rules=[
    Rule(
    name=r.get("name", "Unnamed"),
    conditions=[
    Condition(**cond) for cond in r.get("conditions", [])
    ],
    actions=r.get("actions", []),
    )
    for r in data.get("rules", [])
    ],
    )
    return rs
