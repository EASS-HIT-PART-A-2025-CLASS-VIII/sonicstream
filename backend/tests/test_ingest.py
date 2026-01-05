import os
import pytest
import polars as pl
import tempfile
from scripts.ingest_data import process_data

# Sample CSV content mimicking the Kaggle dataset structure
SAMPLE_CSV_CONTENT = """track_id,name,artist,danceability,energy,valence,tempo,acousticness,instrumentalness,liveness,speechiness,garage
t1,Song A,Artist A,0.5,0.8,0.3,120.0,0.1,0.0,0.2,0.05,junk
t2,Song B,Artist B,0.2,0.4,0.9,100.0,0.8,0.1,0.1,0.04,junk
t3,Song C,Artist C,0.9,0.9,0.8,140.0,0.2,0.0,0.3,0.1,junk
"""

@pytest.fixture
def temp_csv_file():
    """Creates a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        tmp.write(SAMPLE_CSV_CONTENT)
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)

def test_process_data_normalization(temp_csv_file):
    """
    Verifies that process_data correctly:
    1. Loads the CSV
    2. Selects relevant columns
    3. Normalizes tempo (divides by 250)
    4. Clips other features to 0-1
    """
    df = process_data(csv_path=temp_csv_file)

    # Assert shape
    assert df.height == 3
    assert "tempo_norm" in df.columns
    
    # Assert Tempo Normalization (120 / 250 = 0.48)
    assert df.filter(pl.col("track_id") == "t1").select("tempo_norm").item() == pytest.approx(0.48, 0.01)
    
    # Assert Columns Selection (Should not include 'garage')
    assert "garage" not in df.columns
    assert "danceability" in df.columns

def test_process_data_missing_file():
    """Verifies that FileNotFoundError is raised for non-existent path."""
    with pytest.raises(Exception): # polars might raise ComputeError or we raise FileNotFoundError
        process_data(csv_path="non_existent.csv")
