import psycopg
from app.schemas import Track
from typing import List, Optional

class RecommendationService:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.conn = conn

    async def get_recommendations(self, track_id: str, limit: int = 10) -> List[Track]:
        """
        Finds similar tracks based on audio feature embeddings.
        """
        async with self.conn.cursor() as cur:
            # 1. Get the embedding for the source track
            await cur.execute("SELECT audio_embedding FROM tracks WHERE track_id = %s", (track_id,))
            result = await cur.fetchone()
            
            if not result:
                return [] # Track not found
            
            embedding = result[0]
            
            # 2. Find nearest neighbors using L2 distance (<->)
            # Exclude the track itself
            await cur.execute("""
                SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
                FROM tracks
                WHERE track_id != %s
                ORDER BY audio_embedding <-> %s
                LIMIT %s
            """, (track_id, embedding, limit))
            
            rows = await cur.fetchall()
            
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
