"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface Track {
    id: string;
    name: string;
    artist: string;
    album?: string;
    cover_url?: string;
}

interface PlayerContextType {
    currentTrack: Track | null;
    isOpen: boolean;
    playTrack: (track: Track) => void;
    closePlayer: () => void;
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export function PlayerProvider({ children }: { children: ReactNode }) {
    const [currentTrack, setCurrentTrack] = useState<Track | null>(null);
    const [isOpen, setIsOpen] = useState(false);

    const playTrack = (track: Track) => {
        setCurrentTrack(track);
        setIsOpen(true);
    };

    const closePlayer = () => {
        setIsOpen(false);
        // Keep currentTrack so we can resume if needed
    };

    return (
        <PlayerContext.Provider value={{ currentTrack, isOpen, playTrack, closePlayer }}>
            {children}
        </PlayerContext.Provider>
    );
}

export function usePlayer() {
    const context = useContext(PlayerContext);
    if (context === undefined) {
        throw new Error("usePlayer must be used within a PlayerProvider");
    }
    return context;
}
