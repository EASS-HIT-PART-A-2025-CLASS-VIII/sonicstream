"use client";

import { usePlayer } from "@/lib/usePlayer";
import { X } from "lucide-react";
import { useEffect } from "react";

export default function SpotifyPlayerModal() {
    const { currentTrack, isOpen, closePlayer } = usePlayer();

    // Close on Escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") closePlayer();
        };
        if (isOpen) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden";
        }
        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "";
        };
    }, [isOpen, closePlayer]);

    if (!isOpen || !currentTrack) return null;

    // Spotify embed URL - plays 30-second preview
    const spotifyEmbedUrl = `https://open.spotify.com/embed/track/${currentTrack.id}?utm_source=generator&theme=0`;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={closePlayer}
            />

            {/* Modal */}
            <div className="relative z-10 w-full max-w-lg mx-4 animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="bg-[#181818] rounded-t-xl px-6 py-4 flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                        <h2 className="text-lg font-bold text-white truncate">
                            {currentTrack.name}
                        </h2>
                        <p className="text-sm text-gray-400 truncate">
                            {currentTrack.artist}
                        </p>
                    </div>
                    <button
                        onClick={closePlayer}
                        className="ml-4 p-2 rounded-full hover:bg-white/10 transition-colors"
                    >
                        <X className="h-6 w-6 text-gray-400 hover:text-white" />
                    </button>
                </div>

                {/* Spotify Embed */}
                <div className="bg-[#121212] rounded-b-xl overflow-hidden">
                    <iframe
                        src={spotifyEmbedUrl}
                        width="100%"
                        height="352"
                        frameBorder="0"
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        loading="lazy"
                        className="rounded-b-xl"
                    />
                </div>
            </div>
        </div>
    );
}
