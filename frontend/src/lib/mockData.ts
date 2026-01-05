export interface AudioFeatures {
    danceability: number;
    energy: number;
    valence: number;
    tempo: number;
    acousticness: number;
}

export interface Track {
    id: string;
    name: string;
    artist: string;
    album: string;
    coverUrl: string;
    duration: number; // in seconds
    audioFeatures: AudioFeatures;
    genre: string;
}

// Generate mock tracks
const genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz', 'Classical', 'R&B', 'Indie'];
const artists = ['The Weeknd', 'Dua Lipa', 'Olivia Rodrigo', 'Doja Cat', 'Lil Nas X', 'Billie Eilish', 'Drake', 'Taylor Swift'];

export const mockTracks: Track[] = Array.from({ length: 100 }, (_, i) => {
    const artist = artists[i % artists.length];
    const genre = genres[i % genres.length];
    return {
        id: `track-${i + 1}`,
        name: `Track ${i + 1}`,
        artist,
        album: `Album ${Math.floor(i / 10) + 1}`,
        coverUrl: `https://ui-avatars.com/api/?name=${encodeURIComponent(artist)}&background=${Math.floor(Math.random() * 16777215).toString(16)}&color=fff&size=300`,
        duration: 180 + Math.floor(Math.random() * 120),
        audioFeatures: {
            danceability: Math.random(),
            energy: Math.random(),
            valence: Math.random(),
            tempo: 80 + Math.random() * 100,
            acousticness: Math.random(),
        },
        genre,
    };
});

export const getTrackById = (id: string): Track | undefined => {
    return mockTracks.find(track => track.id === id);
};

export const getRecommendedTracks = (trackId: string, limit: number = 20): Track[] => {
    const track = getTrackById(trackId);
    if (!track) return [];

    // Simple recommendation: find tracks with similar audio features
    return mockTracks
        .filter(t => t.id !== trackId)
        .map(t => ({
            ...t,
            similarity: calculateSimilarity(track.audioFeatures, t.audioFeatures),
        }))
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, limit);
};

function calculateSimilarity(a: AudioFeatures, b: AudioFeatures): number {
    const diff = Math.abs(a.danceability - b.danceability) +
        Math.abs(a.energy - b.energy) +
        Math.abs(a.valence - b.valence) +
        Math.abs(a.acousticness - b.acousticness);
    return 1 - (diff / 4);
}

export const getDiscoveryTracks = (page: number = 0, pageSize: number = 20): Track[] => {
    const start = page * pageSize;
    return mockTracks.slice(start, start + pageSize);
};
