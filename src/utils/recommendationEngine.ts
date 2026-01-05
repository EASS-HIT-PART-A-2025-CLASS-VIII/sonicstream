import Papa from 'papaparse';

export interface Track {
    track_name: string;
    artist_name: string;
    album_name: string;
    genre: string;
    [key: string]: string | number | undefined;
}

export interface Recommendation extends Track {
    score?: number;
}

export interface Album {
    name: string;
    artist: string;
    coverUrl: string;
}

let dataset: Track[] = [];

export const loadDataset = async (url: string = '/dataset.csv'): Promise<Track[]> => {
    return new Promise((resolve, reject) => {
        Papa.parse(url, {
            download: true,
            header: true,
            complete: (results) => {
                console.log('Dataset loaded:', results.data.length, 'records');
                dataset = results.data as Track[];
                resolve(dataset);
            },
            error: (error: Error) => {
                console.error('Error loading dataset:', error);
                reject(error);
            },
        });
    });
};

export const getRecommendations = (selectedAlbums: Album[]): Recommendation[] => {
    if (!dataset || dataset.length === 0) {
        console.warn('Dataset not loaded, returning empty suggestions');
        return [];
    }

    // Simple Content-Based Filtering Logic
    // 1. Identify genres/artists from selected albums
    const userPreferences = {
        genres: new Set<string>(),
        artists: new Set<string>(),
    };

    selectedAlbums.forEach((album) => {
        const albumTracks = dataset.filter(track => track.album_name === album.name);
        albumTracks.forEach(track => {
            if (track.genre) userPreferences.genres.add(track.genre);
            if (track.artist_name) userPreferences.artists.add(track.artist_name);
        });
    });

    // 2. Score other tracks
    const suggestions = dataset
        .filter(track => !selectedAlbums.some(album => album.name === track.album_name)) // Exclude selected albums
        .map(track => {
            let score = 0;
            if (userPreferences.genres.has(track.genre)) score += 2;
            if (userPreferences.artists.has(track.artist_name)) score += 3;
            // Add randomness to shuffle results a bit
            score += Math.random();
            return { ...track, score };
        })
        .sort((a, b) => (b.score || 0) - (a.score || 0))
        .slice(0, 20); // Top 20 suggestions

    return suggestions;
};

export const getUniqueAlbums = (): Album[] => {
    const albums = new Map<string, Album>();
    dataset.forEach(track => {
        if (track.album_name && !albums.has(track.album_name)) {
            albums.set(track.album_name, {
                name: track.album_name,
                artist: track.artist_name,
                coverUrl: \`https://ui-avatars.com/api/?name=\${encodeURIComponent(track.album_name)}&background=random\`,
      });
    }
  });
  return Array.from(albums.values());
};
