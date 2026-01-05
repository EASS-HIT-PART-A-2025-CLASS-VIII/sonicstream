"use client"

import { useState, useEffect } from 'react';
import { Track } from './mockData';

const FAVORITES_KEY = 'music-discovery-favorites';

export function useFavorites() {
    const [favorites, setFavorites] = useState<Track[]>([]);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        // Load favorites from localStorage
        const stored = localStorage.getItem(FAVORITES_KEY);
        if (stored) {
            try {
                setFavorites(JSON.parse(stored));
            } catch (e) {
                console.error('Failed to parse favorites:', e);
            }
        }
        setIsLoaded(true);
    }, []);

    const addFavorite = (track: Track) => {
        const newFavorites = [...favorites, track];
        setFavorites(newFavorites);
        localStorage.setItem(FAVORITES_KEY, JSON.stringify(newFavorites));
    };

    const removeFavorite = (trackId: string) => {
        const newFavorites = favorites.filter(t => t.id !== trackId);
        setFavorites(newFavorites);
        localStorage.setItem(FAVORITES_KEY, JSON.stringify(newFavorites));
    };

    const toggleFavorite = (track: Track) => {
        if (isFavorite(track.id)) {
            removeFavorite(track.id);
        } else {
            addFavorite(track);
        }
    };

    const isFavorite = (trackId: string) => {
        return favorites.some(t => t.id === trackId);
    };

    return {
        favorites,
        isLoaded,
        addFavorite,
        removeFavorite,
        toggleFavorite,
        isFavorite,
    };
}
