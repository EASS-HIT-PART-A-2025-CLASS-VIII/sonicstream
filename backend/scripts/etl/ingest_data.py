import os
import polars as pl
import numpy as np
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector

"""
Script: ingest_data.py
Description:
    Raw Data Ingestion Pipeline.
    1. Downloads the 'maltegrosse/8-m-spotify-tracks-genre-audio-features' dataset from Kaggle.
    2. Uses Polars to efficiently load and normalize the CSV data.
    3. Bulk inserts the cleaned data into PostgreSQL using the COPY command.
    
    This is the first step in populating the system if starting from scratch.

Usage:
    python backend/scripts/etl/ingest_data.py
    
    Requirements:
    - KAGGLE_USERNAME and KAGGLE_KEY environment variables.
"""

# Load environment variables
load_dotenv()

DATASET_NAME = "maltegrosse/8-m-spotify-tracks-genre-audio-features"
DOWNLOAD_PATH = "./data_cache"
CSV_FILENAME = "tracks.csv" # Adjust based on actual file name in dataset
DB_CONN_STRING = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin')}@localhost:5432/{os.getenv('POSTGRES_DB', 'music_discovery')}"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg.connect(DB_CONN_STRING, autocommit=True)
    return conn

def init_db():
    """Initializes the database schema with pgvector extension."""
    print("🐘 Initializing Database Schema...")
    with get_db_connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create tracks table
        # We will store the 5 key audio features as a 5-dim vector
        conn.execute("""
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
            )
        """)
        
        # Create HNSW index for fast similarity search
        conn.execute("""
            CREATE INDEX IF NOT EXISTS tracks_embedding_idx 
            ON tracks USING hnsw (audio_embedding vector_l2_ops)
        """)
    print("✅ Database Schema Initialized.")

def download_dataset():
    """
    Authenticates with Kaggle and downloads the dataset.
    Requires KAGGLE_USERNAME and KAGGLE_KEY env vars.
    """
    print(f"🚀 Authenticating with Kaggle...")
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    print(f"⬇️ Downloading dataset: {DATASET_NAME}...")
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    
    api.dataset_download_files(DATASET_NAME, path=DOWNLOAD_PATH, unzip=True)
    print("✅ Download complete.")

def process_data(csv_path: str = None):
    """
    Loads data using Polars, performs cleaning and normalization.
    Args:
        csv_path: Optional path to specific CSV file. If None, auto-discovers in DOWNLOAD_PATH.
    """
    if csv_path is None:
        csv_path = os.path.join(DOWNLOAD_PATH, CSV_FILENAME)
        # Check if file exists, if not, find the likely csv
        if not os.path.exists(csv_path):
            if not os.path.exists(DOWNLOAD_PATH):
                 raise FileNotFoundError(f"Download path not found: {DOWNLOAD_PATH}")
            files = [f for f in os.listdir(DOWNLOAD_PATH) if f.endswith('.csv')]
            if not files:
                raise FileNotFoundError("No CSV file found in download path.")
            csv_path = os.path.join(DOWNLOAD_PATH, files[0])
            print(f"ℹ️ Found CSV file: {csv_path}")

    print(f"⚡ Loading data with Polars from {csv_path}...")
    # Scan CSV for lazy evaluation optimization
    q = pl.scan_csv(csv_path, ignore_errors=True)


    # 1. Select Key Columns
    # Assuming standard spotify feature names. Adjust if dataset differs.
    key_features = [
        "track_id", "name", "artist", "danceability", "energy", 
        "valence", "tempo", "acousticness", "instrumentalness", "liveness", "speechiness"
    ]
    
    print("🧹 Cleaning and Normalizing...")
    
    # Transformation Pipeline
    schema_cols = q.collect_schema().names()
    processed_df = (
        q
        .select([
            pl.col(c) for c in key_features if c in schema_cols
        ] if 'track_id' in schema_cols else pl.all()) # Fallback if columns unknown 
        .drop_nulls()
        .unique(subset=["track_id"]) # Deduplicate
        .with_columns([
            # Normalize Tempo (0-250 approx range) -> 0-1
            (pl.col("tempo") / 250.0).clip(0, 1).alias("tempo_norm"),
            # Ensure other features are 0-1
            pl.col("danceability").clip(0, 1),
            pl.col("energy").clip(0, 1),
            pl.col("valence").clip(0, 1),
            pl.col("acousticness").clip(0, 1),
        ])
    ).collect()

    print(f"✅ Data Processed. Rows: {processed_df.height}")
    return processed_df

def insert_data(df: pl.DataFrame):
    """
    Inserts data into PostgreSQL using high-performance COPY.
    """
    print("💾 Starting DB Insert...")
    
    # We need to construct the embedding vector for each row
    # Polars doesn't support 'list of floats' natively well for DB export without some conversion

    print("⚙️  Preparing vectors...")
    feature_cols = ["danceability", "energy", "valence", "tempo_norm", "acousticness"]
    
    rows = df.iter_rows(named=True)
    
    count = 0
    BATCH_SIZE = 10000
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            batch_buffer = []
            
            print(f"🔄 Starting Batched Insert (Commit every {BATCH_SIZE} rows)...")
            
            for row in rows:
                # pgvector expects '[1.0,2.0,3.0]' string format for COPY
                embedding = [row[c] for c in feature_cols]
                embedding_str = str(embedding)
                
                batch_buffer.append((
                   row["track_id"],
                    row["name"],
                    row["artist"],
                    row["danceability"],
                    row["energy"],
                    row["valence"],
                    row["tempo"], 
                    row["acousticness"],
                    embedding_str
                ))
                
                if len(batch_buffer) >= BATCH_SIZE:
                    with cur.copy("COPY tracks (track_id, name, artist, danceability, energy, valence, tempo, acousticness, audio_embedding) FROM STDIN") as copy:
                        for item in batch_buffer:
                            copy.write_row(item)
                    conn.commit() # <--- Commit this batch so it's visible!
                    count += len(batch_buffer)
                    print(f"   ✅ Committed {count} rows...")
                    batch_buffer = []

            # Insert remaining
            if batch_buffer:
                with cur.copy("COPY tracks (track_id, name, artist, danceability, energy, valence, tempo, acousticness, audio_embedding) FROM STDIN") as copy:
                        for item in batch_buffer:
                            copy.write_row(item)
                conn.commit()
                count += len(batch_buffer)

    print(f"✅ Insertion Complete. Total: {count}")

if __name__ == "__main__":
    try:
        # 1. Setup DB
        try:
            init_db()
        except Exception as e:
            print(f"⚠️  Database init failed (is DB running?): {e}") 
            # We continue only if we assume it's already running or we want to test just processing
            
        # 2. Download Data
        # download_dataset() 
        if not os.path.exists(DOWNLOAD_PATH):
             download_dataset()
        
        # 3. Process Data
        df = process_data()
        
        # 4. Insert Data
        insert_data(df)
        
    except Exception as e:
        print(f"❌ Error: {e}")
