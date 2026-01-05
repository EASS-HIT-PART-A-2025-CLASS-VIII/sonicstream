"use client";

import { motion } from 'framer-motion';
import { Album } from '@/utils/recommendationEngine';
import styles from './AlbumSelector.module.css';

interface AlbumSelectorProps {
    albums: Album[];
    selectedAlbums: Album[];
    onToggleAlbum: (album: Album) => void;
}

export default function AlbumSelector({ albums, selectedAlbums, onToggleAlbum }: AlbumSelectorProps) {
    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Select Your Favorite Albums</h2>
            <div className={styles.grid}>
                {albums.map((album) => {
                    const isSelected = selectedAlbums.some(a => a.name === album.name);
                    return (
                        <motion.div
                            key={album.name}
                            className={`${styles.card} ${isSelected ? styles.selected : ''}`}
                            onClick={() => onToggleAlbum(album)}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div
                                className={styles.cover}
                                style={{ backgroundColor: stringToColor(album.name) }}
                            >
                                {/* Fallback for cover image */}
                                <span className={styles.initial}>{album.name.charAt(0)}</span>
                            </div>
                            <div className={styles.info}>
                                <h3 className={styles.albumName}>{album.name}</h3>
                                <p className={styles.artistName}>{album.artist}</p>
                            </div>
                            {isSelected && <div className={styles.checkmark}>✓</div>}
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}

// Helper to generate consistent colors from strings
function stringToColor(str: string) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const c = (hash & 0x00ffffff).toString(16).toUpperCase();
    return '#' + '00000'.substring(0, 6 - c.length) + c;
}
