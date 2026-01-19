
import psycopg
import os

try:
    conn = psycopg.connect("postgresql://admin:admin@localhost:5432/music_discovery")
    cur = conn.cursor()
    
    # Check correlation between track count and popularity
    print("Popularity vs Track Count (Top 20 by Count):")
    cur.execute("""
        SELECT a.name, a.popularity, count(t.track_id) as track_count 
        FROM albums a
        JOIN tracks t ON t.album = a.name AND t.artist = a.artist
        GROUP BY a.album_id, a.name, a.popularity
        ORDER BY track_count DESC
        LIMIT 20
    """)
    for row in cur.fetchall():
        print(f"Album: {row[0]}, Pop: {row[1]}, Tracks: {row[2]}")
        
    # Check average popularity for different track count buckets
    print("\nAvg Popularity by Track Count Bucket:")
    cur.execute("""
        WITH counts AS (
            SELECT a.popularity, count(t.track_id) as track_count 
            FROM albums a
            JOIN tracks t ON t.album = a.name AND t.artist = a.artist
            GROUP BY a.album_id, a.popularity
        )
        SELECT 
            CASE 
                WHEN track_count < 5 THEN '1-4 tracks'
                WHEN track_count < 10 THEN '5-9 tracks'
                WHEN track_count < 15 THEN '10-14 tracks'
                ELSE '15+ tracks'
            END as bucket,
            AVG(popularity) as avg_pop,
            COUNT(*) as album_count
        FROM counts
        GROUP BY 1
        ORDER BY avg_pop DESC
    """)
    for row in cur.fetchall():
        print(f"Bucket: {row[0]}, Avg Pop: {row[1]:.1f}, Count: {row[2]}")

except Exception as e:
    print(f"Error: {e}")
