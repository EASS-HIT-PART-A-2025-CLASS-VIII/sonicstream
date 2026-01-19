import psycopg
import os
from dotenv import load_dotenv

"""
Script: create_albums_table.py
Description:
    Creates the `albums` table by aggregating data from the `tracks` table.
    The albums table contains:
    - album_id: Unique identifier (album name from tracks)
    - name: Album name
    - artist: Primary artist
    - popularity: Average popularity across tracks
    - avg_embedding: Average audio features vector (5D)
    
Usage:
    python backend/scripts/seeding/create_albums_table.py
"""

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')  # 'db' for Docker, 'localhost' for local
PG_DSN = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@{POSTGRES_HOST}:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"

def create_albums_table():
    print("🎵 Creating albums table from tracks with enhanced features...")
    
    try:
        conn = psycopg.connect(PG_DSN, autocommit=False)
        print("✅ Connected to Postgres.")
        
        with conn.cursor() as cur:
            # 1. Drop existing albums table
            cur.execute("DROP TABLE IF EXISTS albums CASCADE")
            print("🗑️  Dropped existing albums table.")
            
            # 2. Get global max popularity for rescaling
            cur.execute("SELECT MAX(popularity) FROM tracks")
            global_max_pop = cur.fetchone()[0] or 1
            print(f"📊 Global Max Popularity in tracks: {global_max_pop}. Using this to rescale to 100.")

            # 3. Create albums table with genre column and 9D embedding
            create_query = """
                CREATE TABLE albums (
                    album_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    popularity INTEGER,
                    genre TEXT,
                    avg_embedding VECTOR(9)
                )
            """
            cur.execute(create_query)
            print("✅ Created albums table schema (9D embeddings + genre).")
            
            # 4. Aggregate track data into albums with pre-weighted features and artist legacy fallback
            # We scale the popularity so that global_max_pop becomes 100
            scale_factor = 100.0 / global_max_pop
            
            insert_query = f"""
                WITH artist_legacy AS (
                    SELECT artist, MAX(popularity) as artist_peak
                    FROM tracks
                    WHERE artist IS NOT NULL
                    GROUP BY artist
                )
                INSERT INTO albums (album_id, name, artist, popularity, genre, avg_embedding)
                SELECT 
                    MD5(t.album || t.artist) as album_id,
                    t.album as name,
                    MIN(t.artist) as artist,
                    -- Normalized Artist Legacy Fallback: 
                    -- We take the raw peak popularity (album or artist*0.8) and scale it to 100.
                    CAST(GREATEST(
                        COALESCE(MAX(t.popularity), 0), 
                        COALESCE(MAX(al.artist_peak), 0) * 0.8
                    ) * {scale_factor} AS INTEGER) as popularity,
                    -- Genre inference
                    CASE 
                        WHEN AVG(t.energy) > 0.75 AND AVG(t.danceability) > 0.65 THEN 'electronic'
                        WHEN AVG(t.acousticness) > 0.6 AND AVG(t.energy) < 0.5 THEN 'acoustic'
                        WHEN AVG(t.energy) > 0.7 AND AVG(t.acousticness) < 0.3 THEN 'rock'
                        WHEN AVG(t.danceability) > 0.65 AND AVG(t.valence) > 0.6 THEN 'pop'
                        WHEN AVG(t.acousticness) > 0.4 AND AVG(t.valence) < 0.4 THEN 'folk'
                        ELSE 'other'
                    END as genre,
                    -- Pre-weighted 9D embedding
                    ARRAY[
                        AVG(t.danceability) * 1.5,
                        AVG(t.energy) * 1.5,
                        AVG(t.valence) * 1.0,
                        AVG(t.acousticness) * 1.2,
                        (AVG(t.tempo) / 250.0) * 0.8,
                        AVG(t.energy * t.danceability) * 1.3,
                        AVG(t.valence * t.energy) * 1.0,
                        AVG(t.acousticness * (1 - t.energy)) * 0.9,
                        AVG(CASE WHEN t.danceability > 0.5 THEN t.tempo / 250.0 ELSE 0.3 END) * 0.7
                    ]::vector as avg_embedding
                FROM tracks t
                JOIN artist_legacy al ON t.artist = al.artist
                WHERE t.album IS NOT NULL AND t.album != ''
                  AND LOWER(t.name) NOT LIKE '%skit%'
                  AND LOWER(t.name) NOT LIKE '%interlude%'
                  AND LOWER(t.name) NOT LIKE '%intro%'
                  AND LOWER(t.name) NOT LIKE '%outro%'
                GROUP BY t.album, t.artist
                HAVING COUNT(*) >= 1
            """
            cur.execute(insert_query)
            
            # 4. Get count
            cur.execute("SELECT COUNT(*) FROM albums")
            count = cur.fetchone()[0]
            
            conn.commit()
            print(f"✅ Created {count} albums with 9D embeddings and genre tags.")
            
            # 5. Show genre distribution
            cur.execute("SELECT genre, COUNT(*) FROM albums GROUP BY genre ORDER BY COUNT(*) DESC")
            genre_dist = cur.fetchall()
            print("\n📊 Genre Distribution:")
            for genre, cnt in genre_dist:
                print(f"   {genre}: {cnt} albums")
            
            # 6. Create index on embeddings for faster similarity search
            cur.execute("CREATE INDEX IF NOT EXISTS idx_albums_embedding ON albums USING ivfflat (avg_embedding vector_cosine_ops)")
            conn.commit()
            print("\n✅ Created cosine similarity index on embeddings.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("🏁 Done.")

if __name__ == "__main__":
    create_albums_table()
