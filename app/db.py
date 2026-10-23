from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings

class Base(DeclarativeBase): pass

_engine = None
_session_factory = None

def get_engine():
    global _engine, _session_factory
    if _engine is None:
        url = get_settings().database_url
        if not url:
            raise RuntimeError("DATABASE_URL is not configured")
        _engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10, pool_recycle=1800)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine

def session_factory():
    get_engine()
    return _session_factory

def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None: _engine.dispose()
    _engine = _session_factory = None
