"use client";

import { usePlayer } from "@/lib/usePlayer";
import { X, ChevronDown, ChevronUp } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

export default function BottomPlayer() {
    const { currentTrack, isOpen, closePlayer } = usePlayer();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // If no track selected, don't render anything
    if (!currentTrack) return null;

    // Spotify embed URL - compact theme
    const spotifyEmbedUrl = `https://open.spotify.com/embed/track/${currentTrack.id}?utm_source=generator&theme=0`;

    return (
        <div
            className={cn(
                "fixed bottom-0 left-0 right-0 z-50 bg-[#181818] border-t border-white/10 transition-transform duration-300 shadow-[0_-4px_20px_rgba(0,0,0,0.5)]",
                !isOpen && "translate-y-full"
            )}
        >
            {/* Collapse/Expand Handle (Optional, strictly speaking user asked for persistent pane) */}
            {/* <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-[#181818] rounded-t-lg px-4 py-1 cursor-pointer border-t border-x border-white/10">
               {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
            </div> */}

            <div className="container mx-auto max-w-screen-xl relative">
                {/* Close Button (Absolute positioned to not interfere with embed layout if possible, or just placed nicely) */}
                <button
                    onClick={closePlayer}
                    className="absolute top-2 right-4 z-10 p-1 rounded-full bg-black/50 hover:bg-white/20 text-white/50 hover:text-white transition-colors"
                >
                    <X className="h-4 w-4" />
                </button>

                <div className="h-[80px] w-full">
                    <iframe
                        src={spotifyEmbedUrl}
                        width="100%"
                        height="80"
                        frameBorder="0"
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        loading="lazy"
                        className="bg-[#181818]"
                    />
                </div>
            </div>
        </div>
    );
}
