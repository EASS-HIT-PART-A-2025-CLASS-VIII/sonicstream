
import psycopg
import os

try:
    conn = psycopg.connect("postgresql://admin:admin@localhost:5432/music_discovery")
    cur = conn.cursor()
    
    print("Checking Linkin Park popularity...")
    cur.execute("SELECT name, popularity FROM albums WHERE artist ILIKE '%Linkin Park%'")
    rows = cur.fetchall()
    for row in rows:
        print(f"Album: {row[0]}, Popularity: {row[1]}")
        
    print("\nChecking Stats:")
    cur.execute("SELECT MIN(popularity), AVG(popularity), MAX(popularity) FROM albums")
    stats = cur.fetchone()
    print(f"Min: {stats[0]}, Avg: {stats[1]:.2f}, Max: {stats[2]}")

except Exception as e:
    print(f"Error: {e}")
