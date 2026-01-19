"use client"

import { useState, useEffect } from "react";
import Image from "next/image";
import { Album } from "@/lib/api";

interface AlbumCardProps {
    album: Album;
    isSelected?: boolean;
    onClick?: () => void;
}

export default function AlbumCard({ album, isSelected = false, onClick }: AlbumCardProps) {
    const [artworkUrl, setArtworkUrl] = useState<string | null>(album.cover_url || null);
    const [isLoadingArt, setIsLoadingArt] = useState(!album.cover_url);

    // Fetch artwork from iTunes if not provided
    useEffect(() => {
        if (!album.cover_url && album.artist) {
            const searchTerm = `${album.artist} ${album.name}`;
            const query = encodeURIComponent(searchTerm);

            fetch(`https://itunes.apple.com/search?term=${query}&entity=album&limit=1`)
                .then(res => res.json())
                .then(data => {
                    if (data.results?.[0]?.artworkUrl100) {
                        const highResUrl = data.results[0].artworkUrl100.replace('100x100bb', '600x600bb');
                        setArtworkUrl(highResUrl);
                    }
                })
                .catch(() => {})
                .finally(() => {
                    setIsLoadingArt(false);
                });
        } else {
            setIsLoadingArt(false);
        }
    }, [album.cover_url, album.artist, album.name]);

    // Fallback placeholder
    const displayUrl = artworkUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(album.name)}&background=1DB954&color=fff&size=300&bold=true`;

    return (
        <div 
            className={`group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-all duration-300 cursor-pointer ${
                isSelected ? 'ring-2 ring-primary scale-95' : ''
            }`}
            onClick={onClick}
        >
            <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg bg-[#282828]">
                {isLoadingArt ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : (
                    <Image
                        src={displayUrl}
                        alt={album.name}
                        width={300}
                        height={300}
                        className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
                        unoptimized
                    />
                )}
                
                {/* Selection indicator */}
                {isSelected && (
                    <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                        <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
                            <svg className="w-6 h-6 text-black" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                        </div>
                    </div>
                )}
            </div>

            <div className="space-y-1">
                <h3 className="font-bold text-white truncate">{album.name}</h3>
                <p className="text-sm text-[#a7a7a7] truncate">{album.artist}</p>
                
                {/* Show similarity badge if available */}
                {(album as any).similarity !== undefined && (
                    <div className="flex items-center gap-2 pt-1">
                        <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary rounded-full">
                            {Math.round((album as any).similarity * 100)}% match
                        </span>
                        {(album as any).reason && (
                            <span className="text-xs text-[#a7a7a7]">{(album as any).reason}</span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
