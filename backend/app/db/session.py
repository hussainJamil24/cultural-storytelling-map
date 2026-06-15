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


def init_db():
    Base.metadata.create_all(bind=engine)

    if engine.url.get_backend_name() != "sqlite":
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    schema_is_stale = False
    for table in Base.metadata.sorted_tables:
        if table.name not in table_names:
            schema_is_stale = True
            break

        existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
        expected_columns = {column.name for column in table.columns}
        if not expected_columns.issubset(existing_columns):
            schema_is_stale = True
            break

    if schema_is_stale:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


# yields one database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
