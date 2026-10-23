from functools import lru_cache
from app.core.config import get_settings
from app.db import session_factory
from app.repositories.memory import MemoryRepository
from app.repositories.postgres import PostgresRepository

@lru_cache
def memory_repository():return MemoryRepository()
def get_repository():
    if get_settings().data_provider=="memory":
        yield memory_repository();return
    session=session_factory()()
    try:yield PostgresRepository(session)
    except Exception:
        session.rollback();raise
    finally:session.close()
