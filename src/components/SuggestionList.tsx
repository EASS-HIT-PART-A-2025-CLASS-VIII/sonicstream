"use client";

import { motion } from 'framer-motion';
import { Recommendation } from '@/utils/recommendationEngine';
import styles from './SuggestionList.module.css';

interface SuggestionListProps {
    suggestions: Recommendation[];
}

export default function SuggestionList({ suggestions }: SuggestionListProps) {
    if (suggestions.length === 0) return null;

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Recommended for You</h2>
            <div className={styles.list}>
                {suggestions.map((track, index) => (
                    <motion.div
                        key={`${track.track_name}-${index}`}
                        className={styles.row}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ backgroundColor: "rgba(255,255,255,0.05)" }}
                    >
                        <div className={styles.rank}>{index + 1}</div>
                        <div className={styles.trackInfo}>
                            <div className={styles.trackName}>{track.track_name}</div>
                            <div className={styles.artistName}>{track.artist_name}</div>
                        </div>
                        <div className={styles.albumName}>{track.album_name}</div>
                        <div className={styles.meta}>
                            <span className={styles.genre}>{track.genre}</span>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
