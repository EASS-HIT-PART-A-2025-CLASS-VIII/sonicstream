"use client"

import { useState, useEffect } from "react";
import { Play } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import api, { Track } from "@/lib/api";

export default function TrendingSection() {
    const [trendingAlbums, setTrendingAlbums] = useState<Track[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadTrending() {
            try {
                const response = await api.getTrendingTracks(10);
                setTrendingAlbums(response.tracks);
            } catch (error) {
                console.error("Failed to load trending tracks:", error);
            } finally {
                setLoading(false);
            }
        }
        loadTrending();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold tracking-tight">Trending Now</h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="bg-[#181818] p-4 rounded-xl animate-pulse">
                            <div className="aspect-square bg-[#282828] rounded-lg mb-4" />
                            <div className="h-4 bg-[#282828] rounded w-3/4 mb-2" />
                            <div className="h-3 bg-[#282828] rounded w-1/2" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Trending Now</h2>
                <Link href="/discovery" className="text-sm font-medium text-muted-foreground hover:text-white transition-colors">
                    See all
                </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                {trendingAlbums.map((track) => (
                    <Link href={`/track/${track.id}`} key={track.id}>
                        <div className="group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-colors duration-300 cursor-pointer">
                            <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg">
                                <Image
                                    src={track.cover_url || `https://ui-avatars.com/api/?name=${track.artist}&background=random&color=fff&size=200`}
                                    alt={track.name}
                                    width={200}
                                    height={200}
                                    className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
                                />
                                <button className="absolute bottom-2 right-2 h-12 w-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 hover:scale-105 hover:bg-green-400">
                                    <Play className="h-6 w-6 text-black fill-black ml-1" />
                                </button>
                            </div>
                            <h3 className="font-bold text-white truncate">{track.name}</h3>
                            <p className="text-sm text-[#a7a7a7] truncate">{track.artist}</p>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}
