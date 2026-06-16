"""SQLAlchemy engine + session factory for MarketLens."""
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./data/MarketLens.db")
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(db_url, connect_args=connect_args, echo=False)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=True, autocommit=False)
    return _SessionLocal


@contextmanager
def get_session() -> Session:
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Create all tables if they don't exist."""
    from app.core.models import Base  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=get_engine())
