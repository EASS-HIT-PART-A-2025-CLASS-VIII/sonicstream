"use client"

import { useState, useEffect } from "react";
import { Play, Heart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Track } from "@/lib/api";
import { useFavorites } from "@/lib/favorites";
import { usePlayer } from "@/lib/usePlayer";

interface TrackCardProps {
    track: Track;
}

export default function TrackCard({ track }: TrackCardProps) {
    const { isFavorite, toggleFavorite } = useFavorites();
    const { playTrack } = usePlayer();
    const [artworkUrl, setArtworkUrl] = useState<string | null>(track.cover_url || null);
    const [isLoadingArt, setIsLoadingArt] = useState(!track.cover_url);

    // Fetch artwork from iTunes if not provided
    useEffect(() => {
        if (!track.cover_url && track.artist) {
            const searchTerm = track.album
                ? `${track.artist} ${track.album}`
                : `${track.artist} ${track.name}`;
            const query = encodeURIComponent(searchTerm);

            fetch(`https://itunes.apple.com/search?term=${query}&entity=album&limit=1`)
                .then(res => res.json())
                .then(data => {
                    console.log(`[Artwork] Search for "${searchTerm}":`, data.results?.[0]?.artworkUrl100 ? "Found" : "Not Found");
                    if (data.results?.[0]?.artworkUrl100) {
                        // Get higher resolution (600x600)
                        const highResUrl = data.results[0].artworkUrl100.replace('100x100bb', '600x600bb');
                        setArtworkUrl(highResUrl);
                    }
                })
                .catch((err) => {
                    console.error(`[Artwork] Error fetching for "${searchTerm}":`, err);
                })
                .finally(() => {
                    setIsLoadingArt(false);
                });
        } else {
            setIsLoadingArt(false);
        }
    }, [track.cover_url, track.artist, track.album, track.name]);

    // Fallback placeholder
    const displayUrl = artworkUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(track.artist)}&background=1DB954&color=fff&size=300&bold=true`;

    // Convert API Track to the format useFavorites expects
    const favoriteTrack = {
        id: track.id,
        name: track.name,
        artist: track.artist,
        album: track.album || "",
        coverUrl: displayUrl,
        duration: track.duration_ms ? Math.floor(track.duration_ms / 1000) : 180,
        audioFeatures: {
            danceability: track.danceability || 0,
            energy: track.energy || 0,
            valence: track.valence || 0,
            tempo: track.tempo || 120,
            acousticness: track.acousticness || 0,
        },
        genre: track.genre || "",
    };

    return (
        <div className="group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-all duration-300 cursor-pointer">
            <Link href={`/track/${track.id}`}>
                <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg bg-[#282828]">
                    {isLoadingArt ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : (
                        <Image
                            src={displayUrl}
                            alt={track.name}
                            width={300}
                            height={300}
                            className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
                            unoptimized
                        />
                    )}
                    <button
                        className="absolute bottom-2 right-2 h-12 w-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 hover:scale-105 hover:bg-green-400"
                        onClick={(e) => {
                            e.preventDefault();
                            playTrack({
                                id: track.id,
                                name: track.name,
                                artist: track.artist,
                                album: track.album || undefined,
                                cover_url: displayUrl
                            });
                        }}
                    >
                        <Play className="h-6 w-6 text-black fill-black ml-1" />
                    </button>
                </div>
            </Link>

            <div className="space-y-1">
                <Link href={`/track/${track.id}`}>
                    <h3 className="font-bold text-white truncate hover:underline">{track.name}</h3>
                </Link>
                <p className="text-sm text-[#a7a7a7] truncate">{track.artist}</p>
                <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-[#a7a7a7]">{track.genre || "Music"}</span>
                    <button
                        className={`transition-colors ${isFavorite(track.id) ? 'text-primary' : 'text-[#a7a7a7] hover:text-white'
                            }`}
                        onClick={(e) => {
                            e.preventDefault();
                            toggleFavorite(favoriteTrack as any);
                        }}
                    >
                        <Heart className={`h-4 w-4 ${isFavorite(track.id) ? 'fill-primary' : ''}`} />
                    </button>
                </div>
            </div>
        </div>
    );
}
