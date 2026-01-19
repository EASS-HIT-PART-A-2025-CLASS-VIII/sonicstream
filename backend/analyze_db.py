
import psycopg
import os

# Connect to DB
conn = psycopg.connect("postgresql://admin:admin@localhost:5432/music_discovery")
cur = conn.cursor()

# Get counts
cur.execute("SELECT count(*) FROM tracks")
tracks = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM albums")
albums = cur.fetchone()[0]

# Get "lost" tracks
cur.execute("SELECT count(*) FROM tracks WHERE album IS NULL OR album = 'Unknown'")
unknown_album_tracks = cur.fetchone()[0]

# Get avg tracks per album
cur.execute("""
    SELECT avg(track_count), min(track_count), max(track_count) 
    FROM (
        SELECT count(*) as track_count 
        FROM tracks 
        WHERE album IS NOT NULL AND album != 'Unknown' 
        GROUP BY album, artist
    ) sub
""")
stats = cur.fetchone()

print(f"Tracks: {tracks}")
print(f"Albums: {albums}")
print(f"Tracks with Unknown Album: {unknown_album_tracks}")
print(f"Avg tracks/album: {stats[0]:.2f}")
print(f"Min tracks/album: {stats[1]}")
print(f"Max tracks/album: {stats[2]}")
