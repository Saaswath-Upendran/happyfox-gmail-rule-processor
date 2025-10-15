from __future__ import annotations
import datetime
from app.rules_engine import evaluate_rule, compile_ruleset
from types import SimpleNamespace


class DummyEmail(SimpleNamespace):
    pass


def test_string_predicates_all_true():
    rs = compile_ruleset({
    "collection_predicate": "All",
    "rules": [
    {
    "name": "r1",
    "conditions": [
    {"field": "From", "predicate": "Contains", "value": "foo"},
    {"field": "Subject", "predicate": "DoesNotContain", "value": "bar"}
    ],
    "actions": []
    }
    ]
    })
    em = DummyEmail(from_addr="Foo <foo@example.com>", subject="Hello world", snippet="", received_at=datetime.datetime.now(datetime.timezone.utc))
    assert evaluate_rule(em, rs.rules[0]) is True




def test_date_predicate_greater_than_days():
    past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=45)
    em = DummyEmail(from_addr="a", subject="b", snippet="c", received_at=past)
    rs = compile_ruleset({
    "collection_predicate": "All",
    "rules": [
    {"name":"r2","conditions":[{"field":"ReceivedAt","predicate":"GreaterThanDays","value":30}],"actions":[]}
    ]
    })
    assert evaluate_rule(em, rs.rules[0]) is True
