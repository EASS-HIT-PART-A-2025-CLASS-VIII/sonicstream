import Papa from 'papaparse';

// Define the shape of our music data
// Expected CSV columns: track_name, artist_name, album_name, genre, etc.

let dataset = [];

export const loadDataset = async (url = '/dataset.csv') => {
  return new Promise((resolve, reject) => {
    Papa.parse(url, {
      download: true,
      header: true,
      complete: (results) => {
        console.log('Dataset loaded:', results.data.length, 'records');
        dataset = results.data;
        resolve(dataset);
      },
      error: (error) => {
        console.error('Error loading dataset:', error);
        reject(error);
      },
    });
  });
};

export const getRecommendations = (selectedAlbums) => {
  if (!dataset || dataset.length === 0) {
    console.warn('Dataset not loaded, returning empty suggestions');
    return [];
  }

  // Simple Content-Based Filtering Logic
  // 1. Identify genres/artists from selected albums
  const userPreferences = {
    genres: new Set(),
    artists: new Set(),
  };

  selectedAlbums.forEach((album) => {
    // efficient lookup if dataset is huge could be improved, 
    // but for now we filter the dataset to find the album metadata
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
    .sort((a, b) => b.score - a.score)
    .slice(0, 20); // Top 20 suggestions

  return suggestions;
};

// Formatting helper to group raw tracks by album for the UI selector
export const getUniqueAlbums = () => {
  const albums = new Map();
  dataset.forEach(track => {
    if (track.album_name && !albums.has(track.album_name)) {
      albums.set(track.album_name, {
        name: track.album_name,
        artist: track.artist_name,
        // In a real app, we'd have cover art URLs. We can generate a placeholder or use a default.
        coverUrl: \`https://ui-avatars.com/api/?name=\${encodeURIComponent(track.album_name)}&background=random\`,
      });
    }
  });
  return Array.from(albums.values());
};
