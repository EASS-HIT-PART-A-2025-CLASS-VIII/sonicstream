"use client"

import { Play, Heart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Track } from "@/lib/mockData";
import { useFavorites } from "@/lib/favorites";

interface TrackCardProps {
    track: Track;
}

export default function TrackCard({ track }: TrackCardProps) {
    const { isFavorite, toggleFavorite } = useFavorites();
    return (
        <div className="group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-all duration-300 cursor-pointer">
            <Link href={`/track/${track.id}`}>
                <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg">
                    <Image
                        src={track.coverUrl}
                        alt={track.name}
                        width={300}
                        height={300}
                        className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
                    />
                    <button
                        className="absolute bottom-2 right-2 h-12 w-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 hover:scale-105 hover:bg-green-400"
                        onClick={(e) => {
                            e.preventDefault();
                            // Play functionality would go here
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
                    <span className="text-xs text-[#a7a7a7]">{track.genre}</span>
                    <button
                        className={`transition-colors ${isFavorite(track.id) ? 'text-primary' : 'text-[#a7a7a7] hover:text-white'
                            }`}
                        onClick={(e) => {
                            e.preventDefault();
                            toggleFavorite(track);
                        }}
                    >
                        <Heart className={`h-4 w-4 ${isFavorite(track.id) ? 'fill-primary' : ''}`} />
                    </button>
                </div>
            </div>
        </div>
    );
}
