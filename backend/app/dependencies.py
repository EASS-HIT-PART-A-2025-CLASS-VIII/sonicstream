import os
import psycopg
from psycopg_pool import AsyncConnectionPool
from typing import AsyncGenerator
from fastapi import Request

# Global pool variable
pool: AsyncConnectionPool = None

def get_db_connection_string() -> str:
    return f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@{os.getenv('POSTGRES_HOST', 'localhost')}:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"

async def init_db_pool():
    """
    Initializes the connection pool. Called on app startup.
    """
    global pool
    conn_str = get_db_connection_string()
    print(f"🔌 Connecting to DB: {conn_str.replace(os.getenv('POSTGRES_PASSWORD', 'admin'), '******')}")
    pool = AsyncConnectionPool(conn_str, open=False, min_size=1, max_size=20)
    await pool.open()
    print("✅ DB Connection Pool Created.")

async def close_db_pool():
    """
    Closes the connection pool. Called on app shutdown.
    """
    global pool
    if pool:
        await pool.close()
        print("🛑 DB Connection Pool Closed.")

async def get_db() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """
    Dependency to get a DB connection from the pool.
    """
    global pool
    if not pool:
        raise RuntimeError("DB Pool not initialized")
    
    async with pool.connection() as conn:
        yield conn
