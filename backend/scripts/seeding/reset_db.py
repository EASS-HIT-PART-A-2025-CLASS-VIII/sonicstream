import psycopg
import os
from dotenv import load_dotenv

"""
Script: reset_db.py
Description:
    Utility to TRUNCATE the 'tracks' table in Postgres.
    
    This effectively wipes all track data but keeps the table schema integrity.
    Useful before a fresh seed run.

Usage:
    python backend/scripts/seeding/reset_db.py
"""

# Load env vars
load_dotenv()

# Config
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@localhost:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"

def reset_db():
    print("🗑️  Resetting Database (Truncating 'tracks' table)...")
    try:
        with psycopg.connect(PG_DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE tracks RESTART IDENTITY CASCADE;")
                print("✅ Table 'tracks' truncated successfully.")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    reset_db()
