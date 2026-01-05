"use client";

import { useEffect, useState } from 'react';
import { loadDataset, getUniqueAlbums, getRecommendations, Album, Recommendation } from '@/utils/recommendationEngine';
import AlbumSelector from '@/components/AlbumSelector';
import SuggestionList from '@/components/SuggestionList';
import styles from './page.module.css';

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [selectedAlbums, setSelectedAlbums] = useState<Album[]>([]);
  const [suggestions, setSuggestions] = useState<Recommendation[]>([]);

  useEffect(() => {
    async function init() {
      try {
        await loadDataset();
        setAlbums(getUniqueAlbums());
      } catch (e) {
        console.error("Failed to load data", e);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const handleToggleAlbum = (album: Album) => {
    setSelectedAlbums(prev => {
      const exists = prev.some(a => a.name === album.name);
      if (exists) {
        return prev.filter(a => a.name !== album.name);
      }
      if (prev.length >= 5) {
        alert("You can select up to 5 albums.");
        return prev;
      }
      return [...prev, album];
    });
  };

  const handleGetSuggestions = () => {
    const results = getRecommendations(selectedAlbums);
    setSuggestions(results);
    // Smooth scroll to suggestions
    setTimeout(() => {
      window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
    }, 100);
  };

  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <h1 className={styles.logo}>Music Discovery</h1>
        <p className={styles.subtitle}>Select up to 5 albums to get personalized recommendations.</p>
      </header>

      {loading ? (
        <div className={styles.loading}>Loading library...</div>
      ) : (
        <>
          <AlbumSelector
            albums={albums}
            selectedAlbums={selectedAlbums}
            onToggleAlbum={handleToggleAlbum}
          />

          <div className={styles.actions}>
            <button
              className={styles.button}
              disabled={selectedAlbums.length === 0}
              onClick={handleGetSuggestions}
            >
              Get Suggestions ({selectedAlbums.length})
            </button>
          </div>

          <SuggestionList suggestions={suggestions} />
        </>
      )}
    </main>
  );
}
