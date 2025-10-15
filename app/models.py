
from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON
# from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.sql import func
from .db import Base


class Email(Base):
    __tablename__ = "emails"


    id = Column(String, primary_key=True)
    thread_id = Column(String, index=True)
    from_addr = Column(String, index=True)
    to_addr = Column(String)
    subject = Column(Text)
    snippet = Column(Text)
    received_at = Column(DateTime(timezone=True), index=True)
    label_ids = Column(JSON, default=list)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RuleRun(Base):
    __tablename__ = "rule_runs"


    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String, index=True)
    message_id = Column(String, index=True)
    matched = Column(Boolean, default=False)
    actions_applied = Column(Text)
    run_at = Column(DateTime(timezone=True), server_default=func.now())
