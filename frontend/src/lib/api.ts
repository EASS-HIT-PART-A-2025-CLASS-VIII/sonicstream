const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface Track {
    id: string;
    name: string;
    artist: string;
    album: string | null;
    genre: string | null;
    duration_ms: number | null;
    danceability: number | null;
    energy: number | null;
    valence: number | null;
    tempo: number | null;
    acousticness: number | null;
    instrumentalness: number | null;
    liveness: number | null;
    speechiness: number | null;
    loudness: number | null;
    cover_url: string | null;
}

export interface TrackListResponse {
    tracks: Track[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
}

export interface SimilarTrack extends Track {
    similarity: number;
}

// ==================== ALBUM TYPES ====================

export interface Album {
    id: string;
    name: string;
    artist: string;
    popularity: number | null;
    cover_url: string | null;
}

export interface AlbumListResponse {
    albums: Album[];
    total: number;
}

export interface SimilarAlbum extends Album {
    similarity: number;
    reason: string | null;
}

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    }

    // ==================== TRACK METHODS ====================

    async getTracks(page: number = 0, pageSize: number = 20): Promise<TrackListResponse> {
        return this.fetch<TrackListResponse>(`/tracks?page=${page}&page_size=${pageSize}`);
    }

    async getTrendingTracks(limit: number = 20): Promise<TrackListResponse> {
        return this.fetch<TrackListResponse>(`/tracks/trending?limit=${limit}`);
    }

    async searchTracks(query: string, page: number = 0, pageSize: number = 20): Promise<TrackListResponse> {
        return this.fetch<TrackListResponse>(
            `/tracks/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`
        );
    }

    async getTrack(id: string): Promise<Track> {
        return this.fetch<Track>(`/tracks/${id}`);
    }

    async getSimilarTracks(id: string, limit: number = 10): Promise<SimilarTrack[]> {
        return this.fetch<SimilarTrack[]>(`/tracks/${id}/similar?limit=${limit}`);
    }

    // ==================== ALBUM METHODS ====================

    async getAlbums(page: number = 0, pageSize: number = 20): Promise<AlbumListResponse> {
        return this.fetch<AlbumListResponse>(`/albums?page=${page}&page_size=${pageSize}`);
    }

    async searchAlbums(query: string, page: number = 0, pageSize: number = 20): Promise<AlbumListResponse> {
        return this.fetch<AlbumListResponse>(
            `/albums/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`
        );
    }

    async getAlbum(id: string): Promise<Album> {
        return this.fetch<Album>(`/albums/${id}`);
    }

    async getAlbumRecommendations(albumId: string, limit: number = 10): Promise<SimilarAlbum[]> {
        return this.fetch<SimilarAlbum[]>('/albums/recommend', {
            method: 'POST',
            body: JSON.stringify({ album_id: albumId, limit }),
        });
    }

    // ==================== HEALTH ====================

    async healthCheck(): Promise<{ status: string }> {
        return this.fetch<{ status: string }>('/health');
    }
}

export const api = new ApiClient();
export default api;

