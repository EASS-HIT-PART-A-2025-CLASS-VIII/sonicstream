from sqlalchemy import create_engine, Column, String, Float, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "spotify.sqlite")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get table info to understand the schema
def get_table_schema():
    with engine.connect() as conn:
        # Get table names
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        schema = {}
        for table in tables:
            table_name = table[0]
            columns = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            schema[table_name] = [{"name": col[1], "type": col[2]} for col in columns]
        return schema
