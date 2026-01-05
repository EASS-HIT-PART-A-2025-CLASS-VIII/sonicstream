import os
import polars as pl
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATASET_NAME = "maltegrosse/8-m-spotify-tracks-genre-audio-features"
DOWNLOAD_PATH = "./data_cache"
CSV_FILENAME = "tracks.csv" # Adjust based on actual file name in dataset

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
    
    # Verify columns exist (eager load for schema check - optimization: read header only)
    # For now, we'll try to select and catch errors or list all columns first
    # robust approach:
    
    print("🧹 Cleaning and Normalizing...")
    
    # Transformation Pipeline
    processed_df = (
        q
        .select([
            pl.col(c) for c in key_features if c in q.columns
        ] if 'track_id' in q.columns else pl.all()) # Fallback if columns unknown 
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

if __name__ == "__main__":
    try:
        # download_dataset() # Commented out for dev to avoid re-downloading every run
        # For first run, uncomment or check existence
        if not os.path.exists(DOWNLOAD_PATH):
             download_dataset()
        
        df = process_data()
        print(df.head())
        
        # Next step: Embedding generation & DB Insert
        
    except Exception as e:
        print(f"❌ Error: {e}")
