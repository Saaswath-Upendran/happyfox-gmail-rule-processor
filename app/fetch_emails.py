from __future__ import annotations
import logging, datetime, email, base64
from typing import Dict, Any
from sqlalchemy import select
from .db import SessionLocal, Base, engine
from .models import Email
from .gmail_client import GmailClient
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)


# Utility to extract headers


def _get_header(payload_headers: list[dict[str, str]], name: str) -> str | None:
    for h in payload_headers:
        if h.get("name") == name:
            return h.get("value")
    return None


# Convert Gmail RFC822 date to aware datetime


def _parse_gmail_date(raw_date: str) -> datetime.datetime | None:
    try:

        dt = parsedate_to_datetime(raw_date)
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None




def fetch_and_store(max_results: int = 100) -> int:
    Base.metadata.create_all(bind=engine)
    client = GmailClient()
    client.authenticate()


    count = 0
    with SessionLocal() as s:
        for msg_id in client.list_message_ids(max_results=max_results):
            msg = client.get_message(msg_id)
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])


            from_addr = _get_header(headers, "From") or ""
            to_addr = _get_header(headers, "To") or ""
            subject = _get_header(headers, "Subject") or ""
            date_raw = _get_header(headers, "Date") or ""
            received_at = _parse_gmail_date(date_raw)
            label_ids = msg.get("labelIds", [])


            snippet = msg.get("snippet", "")


            # Determine read status (absence of UNREAD label)
            is_read = "UNREAD" not in (label_ids or [])


            exists = s.get(Email, msg_id)
            if exists:
            # Update labels/read state if changed
                exists.label_ids = label_ids
                exists.is_read = is_read
            else:
                e = Email(
                id=msg_id,
                thread_id=msg.get("threadId"),
                from_addr=from_addr,
                to_addr=to_addr,
                subject=subject,
                snippet=snippet,
                received_at=received_at,
                label_ids=label_ids,
                is_read=is_read,
                )
                s.add(e)
                count += 1
        s.commit()
    logger.info("Fetched and stored %s new emails", count)
    return count
