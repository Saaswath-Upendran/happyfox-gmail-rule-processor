from __future__ import annotations
import json, logging
from typing import Dict, Any, List
from sqlalchemy import select
from .db import SessionLocal
from .models import Email, RuleRun
from .rules_engine import compile_ruleset, evaluate_rule
from .gmail_client import GmailClient


logger = logging.getLogger(__name__)


# Map high-level actions to Gmail label changes
_DEF_LABELS = {
"INBOX": "INBOX",
"READ_LATER": None, # Custom label; if missing, created implicitly by Gmail upon use.
"PROMOTIONS": None,
}


# Helper to derive label ops for actions


def _labels_for_actions(actions: List[Dict[str, Any]], current: List[str]) -> tuple[list[str], list[str]]:
    add, remove = set(), set()
    for a in actions:
        t = a.get("type")
        if t == "MarkAsRead":
            remove.add("UNREAD")
        elif t == "MarkAsUnread":
            add.add("UNREAD")
        elif t == "Move":
            label = a.get("label")
    if label:
        add.add(label)
    else:
        logger.warning("Unknown action type: %s", t)
    return list(add), list(remove)




def process_with_rules(rules_path: str) -> int:
    client = GmailClient()
    client.authenticate()


    with open(rules_path, "r", encoding="utf-8") as f:
        rs = compile_ruleset(json.load(f))


    applied = 0
    with SessionLocal() as s:
        emails = s.scalars(select(Email)).all()
        for em in emails:
            for r in rs.rules:
                try:
                    matched = evaluate_rule(em, r)
                except Exception as ex:
                    logger.exception("Rule '%s' evaluation failed: %s", r.name, ex)
                    continue


                if matched:
                    add, remove = _labels_for_actions(r.actions, em.label_ids or [])
                    if add or remove:
                        add_ids = [client.get_label_id(x) for x in add]
                        remove_ids = remove  # built-in ones like UNREAD are fine
                        client.modify_message_labels(em.id, add=add_ids, remove=remove_ids)
                    em.label_ids = [*(em.label_ids or []), *add]
                    em.label_ids = [x for x in em.label_ids if x not in remove]
                    em.is_read = "UNREAD" not in em.label_ids
                    s.add(RuleRun(rule_name=r.name, message_id=em.id, matched=True, actions_applied=json.dumps(r.actions)))
                    applied += 1
            s.commit()
    logger.info("Applied actions to %s messages", applied)
    return applied
