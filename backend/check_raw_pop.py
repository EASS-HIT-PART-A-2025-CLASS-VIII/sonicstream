
import psycopg
import os

try:
    conn = psycopg.connect("postgresql://admin:admin@localhost:5432/music_discovery")
    cur = conn.cursor()
    
    print("Checking Raw Track Popularity for Linkin Park:")
    cur.execute("""
        SELECT name, popularity 
        FROM tracks 
        WHERE artist ILIKE '%Linkin Park%' 
        ORDER BY popularity DESC 
        LIMIT 20
    """)
    rows = cur.fetchall()
    if not rows:
        print("No tracks found for Linkin Park.")
    else:
        for row in rows:
            print(f"Track: {row[0]}, Pop: {row[1]}")

except Exception as e:
    print(f"Error: {e}")
