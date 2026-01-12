import sqlite3
import psycopg
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Load env vars
load_dotenv()

# Config
SQLITE_DB = "spotify.sqlite"
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@{POSTGRES_HOST}:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"
BATCH_SIZE = 1000  # Commit every N rows
ROW_LIMIT = 10000  # Total rows to seed

def run_dev_seed():
    print(f"🌱 Starting DEV SEED (Limit: {ROW_LIMIT} rows)...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ ERROR: {SQLITE_DB} not found in {os.getcwd()}")
        return

    # Check for popularity in Source DB first
    has_popularity = False
    try:
        tmp_conn = sqlite3.connect(SQLITE_DB)
        cursor = tmp_conn.execute("PRAGMA table_info(tracks)")
        columns = [r[1] for r in cursor.fetchall()]
        if 'popularity' in columns:
            has_popularity = True
            print("⭐ Found 'popularity' column! Converting seeding to 'Top Popular' mode.")
        tmp_conn.close()
    except Exception:
        pass

    # 1. Connect to Postgres & Init Schema
    try:
        pg_conn = psycopg.connect(PG_DSN, autocommit=False) # Manual commit control
        print("✅ Connected to Postgres.")
        
        with pg_conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Drop table first to allow schema change
            cur.execute("DROP TABLE IF EXISTS tracks CASCADE")
            
            create_query = """
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT,
                    artist TEXT,
                    danceability FLOAT,
                    energy FLOAT,
                    valence FLOAT,
                    tempo FLOAT,
                    acousticness FLOAT,
                    audio_embedding VECTOR(5)
            """
            
            if has_popularity:
                create_query += ", popularity INTEGER"
                
            create_query += ")"
            
            cur.execute(create_query)
        pg_conn.commit()
    except Exception as e:
        print(f"❌ Postgres Connection Error: {e}")
        return

    # 2. Connect to SQLite & Extract Real Data
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.text_factory = lambda b: b.decode(errors="ignore")
        
        # Build Query
        select_clause = """
            SELECT 
                t.id, 
                t.name, 
                GROUP_CONCAT(a.name, ', ') as artist, 
                MAX(af.danceability), 
                MAX(af.energy), 
                MAX(af.valence), 
                MAX(af.tempo), 
                MAX(af.acousticness)
        """
        
        if has_popularity:
            select_clause += ", MAX(t.popularity)"
            
        join_clause = """
            FROM tracks t
            JOIN audio_features af ON t.id = af.id
            JOIN r_track_artist rta ON t.id = rta.track_id
            JOIN artists a ON rta.artist_id = a.id
            GROUP BY t.id
        """
        
        order_clause = ""
        if has_popularity:
            order_clause = "ORDER BY MAX(t.popularity) DESC"
            
        limit_clause = f"LIMIT {ROW_LIMIT}"
        
        final_query = f"{select_clause} {join_clause} {order_clause} {limit_clause}"
        
        print(f"⚡ Executing SQLite JOIN Query (fetching {ROW_LIMIT} rows)...")
        cursor = sqlite_conn.cursor()
        cursor.execute(final_query)
        
        # 3. Stream & Insert with Progress Bar
        total_inserted = 0
        
        # Initialize progress bar
        pbar = tqdm(total=ROW_LIMIT, unit="rows", desc="🚀 Seeding")

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            clean_rows = []
            for r in rows:
                # r = (id, track_name, artist_name, dance, energy, valence, tempo, acoustic, [popularity])
                track_id = r[0]
                name = r[1]
                artist = r[2] or "Unknown"
                dance = r[3] or 0.5
                energy = r[4] or 0.5
                valence = r[5] or 0.5
                tempo = r[6] or 120.0
                acoustic = r[7] or 0.5
                
                # Normalize tempo for embedding (0-250 approx range)
                tempo_norm = min(max(tempo / 250.0, 0.0), 1.0)
                embedding = [dance, energy, valence, tempo_norm, acoustic]
                
                row_data = [
                    track_id, 
                    name, 
                    artist, 
                    dance, 
                    energy, 
                    valence, 
                    tempo, 
                    acoustic, 
                    str(embedding)
                ]
                
                if has_popularity:
                    row_data.append(r[8] or 0) # popularity
                
                clean_rows.append(tuple(row_data))
            
            # Insert Batch to Postgres
            with pg_conn.cursor() as cur:
                cols = "track_id, name, artist, danceability, energy, valence, tempo, acousticness, audio_embedding"
                if has_popularity:
                    cols += ", popularity"
                    
                with cur.copy(f"COPY tracks ({cols}) FROM STDIN") as copy:
                    for row in clean_rows:
                        copy.write_row(row)
            
            # COMMIT THIS BATCH so it is visible immediately
            pg_conn.commit()
            
            total_inserted += len(rows)
            pbar.update(len(rows))
            
            if total_inserted >= ROW_LIMIT:
                break

        pbar.close()

    except Exception as e:
        print(f"\n❌ Error during seed: {e}")
        if 'pg_conn' in locals(): pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()
        print(f"\n🏁 Finished. Total Rows Inserted: {total_inserted}")

if __name__ == "__main__":
    run_dev_seed()
