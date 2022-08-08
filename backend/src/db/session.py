from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

if settings.DATABASE_URI.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URI, connect_args={"check_same_thread": False}, echo=settings.PRINT_SQL)
else:
    engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True, echo=settings.PRINT_SQL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, )
