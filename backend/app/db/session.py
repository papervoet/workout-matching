# backend/app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import DATABASE_URL

# SQLite의 경우에만 필요한 옵션
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
