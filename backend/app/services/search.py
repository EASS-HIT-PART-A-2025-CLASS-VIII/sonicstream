import psycopg
from app.schemas import Track
from typing import List

class SearchService:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.conn = conn

    async def search_tracks(self, query: str, limit: int = 10) -> List[Track]:
        """
        Searches for tracks by title or artist using fuzzy matching.
        """
        async with self.conn.cursor() as cur:
            # Using ILIKE for broad matching. 
            # For strict Trigram similarity sorting, we would need 'pg_trgm' extension and ORDER BY similarity(name, query)
            # For now, simple standard matching is robust enough for Phase 2 start.
            
            # Optimization: We select specific columns to match the Track schema
            await cur.execute("""
                SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
                FROM tracks
                WHERE name ILIKE %s OR artist ILIKE %s
                LIMIT %s
            """, (f"%{query}%", f"%{query}%", limit))
            
            rows = await cur.fetchall()
            
            # Convert to Pydantic models
            tracks = [
                Track(
                    track_id=row[0],
                    name=row[1],
                    artist=row[2],
                    danceability=row[3],
                    energy=row[4],
                    valence=row[5],
                    tempo=row[6],
                    acousticness=row[7]
                ) for row in rows
            ]
            return tracks
