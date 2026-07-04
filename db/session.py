from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    echo=Config.DEBUG,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


@contextmanager
def get_session():
    """
    Context manager that yields a SQLAlchemy session and guarantees
    commit/rollback/close, so callers never have to manage that by hand.

    Usage:
        with get_session() as session:
            session.add(obj)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
