from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Config
# Use the same connection string logic as dev_seed.py
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'music_discovery')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

# Create Engine
# pool_pre_ping=True handles disconnected connections gracefully
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get table info to understand the schema (Updated for Postgres)
def get_table_schema():
    with engine.connect() as conn:
        # Get table names (public schema)
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = conn.execute(query).fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            # Get columns
            col_query = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = :table_name
            """)
            columns = conn.execute(col_query, {"table_name": table_name}).fetchall()
            schema[table_name] = [{"name": col[0], "type": col[1]} for col in columns]
            
        return schema
