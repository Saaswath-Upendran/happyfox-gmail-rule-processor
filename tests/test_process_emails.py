from __future__ import annotations
import json
from types import SimpleNamespace
from app.process_emails import _labels_for_actions




def test_labels_for_actions_mark_read_and_move():
    actions = [
    {"type": "MarkAsRead"},
    {"type": "Move", "label": "READ_LATER"}
    ]
    add, remove = _labels_for_actions(actions, current=["INBOX", "UNREAD"])
    assert "UNREAD" in remove
    assert "READ_LATER" in add
