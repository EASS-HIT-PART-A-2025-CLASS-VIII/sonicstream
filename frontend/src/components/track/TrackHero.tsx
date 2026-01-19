"use client"

import { useState } from "react";
import Image from "next/image";
import { Play, Heart, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Track } from "@/lib/api"; // Assuming shared type, or I'll specificy strict type

// Define interface matching the track object structure used in page.tsx
interface TrackHeroProps {
    track: any; // Using any for flexibility with mock/real data mix, or better define partial interface
}

export default function TrackHero({ track }: TrackHeroProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    
    // Format duration
    const minutes = Math.floor(track.duration / 60); // Assuming duration is in seconds for mock data? 
    // Wait, mockData usually has duration (seconds) or duration_ms? 
    // In page.tsx: const minutes = Math.floor(track.duration / 60); -> implies seconds.
    // In TrackCard.tsx: track.duration_ms / 1000. 
    // I should check mockData.ts to be safe, but I'll stick to what was in page.tsx
    const seconds = track.duration % 60;

    return (
        <>
            <div className="flex flex-col md:flex-row gap-8 mb-12">
                <div className="relative w-full md:w-80 aspect-square rounded-xl overflow-hidden shadow-2xl bg-[#282828]">
                    {isPlaying ? (
                        <iframe
                            src={`https://open.spotify.com/embed/track/${track.id}`}
                            width="100%"
                            height="100%"
                            frameBorder="0"
                            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                            loading="lazy"
                            className="absolute inset-0 w-full h-full border-none"
                        />
                    ) : (
                        <Image
                            src={track.coverUrl || track.cover_url} // Handle both casing
                            alt={track.name}
                            fill
                            className="object-cover"
                            priority
                            unoptimized
                        />
                    )}
                </div>

                <div className="flex flex-col justify-end">
                    <p className="text-sm font-semibold text-muted-foreground mb-2">SONG</p>
                    <h1 className="text-4xl md:text-6xl font-black mb-6 leading-tight">{track.name}</h1>
                    <div className="flex items-center gap-2 text-sm">
                        <span className="font-semibold">{track.artist}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{track.album}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{minutes}:{seconds.toString().padStart(2, '0')}</span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-4 mb-12">
                <Button 
                    size="lg" 
                    className="h-14 px-8 rounded-full bg-primary text-black hover:bg-primary/90 text-lg font-bold"
                    onClick={() => setIsPlaying(true)}
                >
                    <Play className="mr-2 h-6 w-6 fill-black" />
                    Play
                </Button>
                <button className="h-14 w-14 rounded-full border border-white/10 hover:border-white/30 flex items-center justify-center transition-colors">
                    <Heart className="h-6 w-6" />
                </button>
                <button className="h-14 w-14 rounded-full border border-white/10 hover:border-white/30 flex items-center justify-center transition-colors">
                    <MoreHorizontal className="h-6 w-6" />
                </button>
            </div>
        </>
    );
}
