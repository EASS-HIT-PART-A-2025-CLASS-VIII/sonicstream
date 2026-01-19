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
TRACK_LIMIT = 10000  # Total tracks to seed
ALBUM_LIMIT = 2000  # Total albums to seed

def run_dev_seed():
    print(f"🌱 Starting DEV SEED (Tracks: {TRACK_LIMIT}, Albums: {ALBUM_LIMIT})...")
    
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
        pg_conn = psycopg.connect(PG_DSN, autocommit=False)
        print("✅ Connected to Postgres.")
        
        with pg_conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Drop tables in order (due to foreign keys)
            cur.execute("DROP TABLE IF EXISTS album_tracks CASCADE")
            cur.execute("DROP TABLE IF EXISTS albums CASCADE")
            cur.execute("DROP TABLE IF EXISTS tracks CASCADE")
            
            # Create tracks table
            create_tracks = """
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT,
                    artist TEXT,
                    album_id TEXT,
                    danceability FLOAT,
                    energy FLOAT,
                    valence FLOAT,
                    tempo FLOAT,
                    acousticness FLOAT,
                    audio_embedding VECTOR(5)
            """
            if has_popularity:
                create_tracks += ", popularity INTEGER"
            create_tracks += ")"
            cur.execute(create_tracks)
            
            # Create albums table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS albums (
                    album_id TEXT PRIMARY KEY,
                    name TEXT,
                    artist TEXT,
                    popularity INTEGER DEFAULT 0,
                    avg_embedding VECTOR(5)
                )
            """)
            
            # Create album_tracks junction table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS album_tracks (
                    album_id TEXT REFERENCES albums(album_id),
                    track_id TEXT REFERENCES tracks(track_id),
                    PRIMARY KEY (album_id, track_id)
                )
            """)
            
            # Create index for similarity search
            cur.execute("CREATE INDEX IF NOT EXISTS idx_albums_embedding ON albums USING ivfflat (avg_embedding vector_l2_ops) WITH (lists = 100)")
            
        pg_conn.commit()
        print("✅ Schema created (tracks, albums, album_tracks).")
    except Exception as e:
        print(f"❌ Postgres Connection Error: {e}")
        return

    total_tracks = 0
    total_albums = 0

    # 2. Connect to SQLite & Extract Data
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.text_factory = lambda b: b.decode(errors="ignore")
        
        # ==================== SEED TRACKS ====================
        print(f"\n📀 Seeding Tracks...")
        
        select_clause = """
            SELECT 
                t.id, 
                t.name, 
                GROUP_CONCAT(a.name) as artist,
                (SELECT rat.album_id FROM r_albums_tracks rat WHERE rat.track_id = t.id LIMIT 1) as album_id,
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
            LEFT JOIN audio_features af ON t.id = af.id
            LEFT JOIN r_track_artist rta ON t.id = rta.track_id
            LEFT JOIN artists a ON rta.artist_id = a.id
            GROUP BY t.id
        """
        
        order_clause = "ORDER BY MAX(t.popularity) DESC" if has_popularity else ""
        limit_clause = f"LIMIT {TRACK_LIMIT}"
        
        final_query = f"{select_clause} {join_clause} {order_clause} {limit_clause}"
        
        cursor = sqlite_conn.cursor()
        cursor.execute(final_query)
        
        total_tracks = 0
        pbar = tqdm(total=TRACK_LIMIT, unit="tracks", desc="🎵 Tracks")

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            clean_rows = []
            for r in rows:
                track_id = r[0]
                name = r[1]
                artist = r[2] or "Unknown"
                album_id = r[3]  # Can be None
                dance = r[4] or 0.5
                energy = r[5] or 0.5
                valence = r[6] or 0.5
                tempo = r[7] or 120.0
                acoustic = r[8] or 0.5
                
                tempo_norm = min(max(tempo / 250.0, 0.0), 1.0)
                embedding = [dance, energy, valence, tempo_norm, acoustic]
                
                row_data = [track_id, name, artist, album_id, dance, energy, valence, tempo, acoustic, str(embedding)]
                
                if has_popularity:
                    row_data.append(r[9] or 0)
                
                clean_rows.append(tuple(row_data))
            
            with pg_conn.cursor() as cur:
                cols = "track_id, name, artist, album_id, danceability, energy, valence, tempo, acousticness, audio_embedding"
                if has_popularity:
                    cols += ", popularity"
                    
                with cur.copy(f"COPY tracks ({cols}) FROM STDIN") as copy:
                    for row in clean_rows:
                        copy.write_row(row)
            
            pg_conn.commit()
            total_tracks += len(rows)
            pbar.update(len(rows))
            
            if total_tracks >= TRACK_LIMIT:
                break

        pbar.close()
        print(f"✅ Inserted {total_tracks} tracks.")
        
        # ==================== SEED ALBUMS ====================
        print(f"\n💿 Seeding Albums...")
        
        album_query = f"""
            SELECT 
                alb.id,
                alb.name,
                GROUP_CONCAT(a.name) as artist,
                MAX(alb.popularity) as popularity,
                AVG(af.danceability) as avg_dance,
                AVG(af.energy) as avg_energy,
                AVG(af.valence) as avg_valence,
                AVG(af.tempo) as avg_tempo,
                AVG(af.acousticness) as avg_acoustic
            FROM albums alb
            JOIN r_albums_tracks rat ON alb.id = rat.album_id
            JOIN tracks t ON rat.track_id = t.id
            LEFT JOIN audio_features af ON t.id = af.id
            LEFT JOIN r_albums_artists raa ON alb.id = raa.album_id
            LEFT JOIN artists a ON raa.artist_id = a.id
            GROUP BY alb.id
            HAVING COUNT(t.id) >= 3
            ORDER BY MAX(alb.popularity) DESC
            LIMIT {ALBUM_LIMIT}
        """
        
        cursor.execute(album_query)
        
        total_albums = 0
        pbar = tqdm(total=ALBUM_LIMIT, unit="albums", desc="💿 Albums")
        
        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            album_rows = []
            for r in rows:
                album_id = r[0]
                name = r[1]
                artist = r[2] or "Unknown"
                popularity = r[3] or 0
                avg_dance = r[4] or 0.5
                avg_energy = r[5] or 0.5
                avg_valence = r[6] or 0.5
                avg_tempo = r[7] or 120.0
                avg_acoustic = r[8] or 0.5
                
                tempo_norm = min(max(avg_tempo / 250.0, 0.0), 1.0)
                avg_embedding = [avg_dance, avg_energy, avg_valence, tempo_norm, avg_acoustic]
                
                album_rows.append((album_id, name, artist, popularity, str(avg_embedding)))
            
            with pg_conn.cursor() as cur:
                with cur.copy("COPY albums (album_id, name, artist, popularity, avg_embedding) FROM STDIN") as copy:
                    for row in album_rows:
                        copy.write_row(row)
            
            pg_conn.commit()
            total_albums += len(rows)
            pbar.update(len(rows))
            
            if total_albums >= ALBUM_LIMIT:
                break
        
        pbar.close()
        print(f"✅ Inserted {total_albums} albums.")
        
        # ==================== SEED ALBUM-TRACK RELATIONS ====================
        print(f"\n🔗 Linking albums to tracks...")
        
        # Get track IDs that exist in Postgres
        with pg_conn.cursor() as cur:
            cur.execute("SELECT track_id FROM tracks")
            pg_track_ids = set(r[0] for r in cur.fetchall())
            cur.execute("SELECT album_id FROM albums")
            pg_album_ids = set(r[0] for r in cur.fetchall())
        
        relation_query = """
            SELECT album_id, track_id FROM r_albums_tracks
        """
        cursor.execute(relation_query)
        
        relation_rows = []
        for r in cursor.fetchall():
            album_id, track_id = r[0], r[1]
            if album_id in pg_album_ids and track_id in pg_track_ids:
                relation_rows.append((album_id, track_id))
        
        with pg_conn.cursor() as cur:
            with cur.copy("COPY album_tracks (album_id, track_id) FROM STDIN") as copy:
                for row in relation_rows:
                    copy.write_row(row)
        
        pg_conn.commit()
        print(f"✅ Created {len(relation_rows)} album-track links.")

    except Exception as e:
        print(f"\n❌ Error during seed: {e}")
        import traceback
        traceback.print_exc()
        if 'pg_conn' in locals(): pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()
        print(f"\n🏁 Finished. Tracks: {total_tracks}, Albums: {total_albums}")

if __name__ == "__main__":
    run_dev_seed()
