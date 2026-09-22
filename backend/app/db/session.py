from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, declarative_base, sessionmaker


# sqlite database file inside backend folder
DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[2] / 'storymap.db'}"

# creates sqlalchemy engine for sqlite database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# creates database sessions for queries and transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for future sqlalchemy models
Base = declarative_base()


def validate_existing_schema(db_engine=None):
    """Check existing tables before issuing any schema-changing statements."""
    db_engine = db_engine if db_engine is not None else engine
    inspector = inspect(db_engine)
    table_names = set(inspector.get_table_names())
    problems = []
    for table in Base.metadata.sorted_tables:
        if table.name not in table_names:
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
        expected_columns = {column.name for column in table.columns}
        missing_columns = sorted(expected_columns - existing_columns)
        if missing_columns:
            problems.append(f"{table.name}: missing {', '.join(missing_columns)}")
    if problems:
        raise RuntimeError(
            "Database schema is incompatible; no tables or data were changed. "
            "Back up this database and migrate it explicitly before starting. "
            + "; ".join(problems)
        )


def init_db(db_engine=None):
    db_engine = db_engine if db_engine is not None else engine
    validate_existing_schema(db_engine)
    Base.metadata.create_all(bind=db_engine)


# yields one database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
