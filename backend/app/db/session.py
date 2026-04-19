from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


# sqlite database file inside backend folder
DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[2] / 'storymap.db'}"

# creates sqlalchemy engine for sqlite database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# creates database sessions for queries and transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for future sqlalchemy models
Base = declarative_base()


# opens and closes a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
