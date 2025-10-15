from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Email




def test_email_model_create_read(tmp_path):
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)


    with Session() as s:
        e = Email(id="mid1", thread_id="t1", from_addr="a@b.com", to_addr="x@y.com", subject="Subj", snippet="Snip")
        s.add(e)
        s.commit()
        got = s.get(Email, "mid1")
        assert got.subject == "Subj"
