import os
import sys
import json
from sqlalchemy import create_engine, text

# Add backend directory to path so we can import app modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

def export_tracks():
    # Force localhost for running script from host machine (WSL) against Docker mapped port
    os.environ["POSTGRES_HOST"] = "localhost"
    
    # Import here after setting env var
    # We construct URL manually here to be safe and independent
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'music_discovery')
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
    
    print(f"Connecting to {DATABASE_URL}...")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Connected! Querying tracks...")
            result = conn.execute(text("""
                SELECT 
                    track_id, 
                    name, 
                    artist, 
                    album, 
                    cover_url, 
                    popularity, 
                    duration_ms, 
                    preview_url,
                    genre,
                    danceability,
                    energy,
                    valence,
                    tempo,
                    acousticness
                FROM tracks
                ORDER BY popularity DESC
                LIMIT 5000 
            """))
            
            tracks = []
            for row in result:
                # Convert row to dict
                track = {
                    "id": row.track_id,
                    "name": row.name,
                    "artist": row.artist,
                    "album": row.album,
                    "cover_url": row.cover_url,
                    "popularity": row.popularity,
                    "duration_ms": row.duration_ms,
                    "preview_url": row.preview_url,
                    "genre": row.genre,
                    "danceability": row.danceability,
                    "energy": row.energy,
                    "valence": row.valence,
                    "tempo": row.tempo,
                    "acousticness": row.acousticness
                }
                tracks.append(track)
            
            print(f"Exported {len(tracks)} tracks.")
            
            # Ensure data directory exists
            output_dir = os.path.join(os.path.dirname(__file__), '../data')
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, 'tracks.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tracks, f, indent=2, ensure_ascii=False)
                
            print(f"Successfully saved to {output_file}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your database container is running and port 5432 is exposed to localhost.")

if __name__ == "__main__":
    export_tracks()
