"use client"

import { Play, Heart } from "lucide-react";
import Image from "next/image";

// Mock Data
const trendingAlbums = [
    { id: 1, title: "After Hours", artist: "The Weeknd", cover: "https://ui-avatars.com/api/?name=After+Hours&background=000&color=fff&size=200" },
    { id: 2, title: "Future Nostalgia", artist: "Dua Lipa", cover: "https://ui-avatars.com/api/?name=Future+Nostalgia&background=e91e63&color=fff&size=200" },
    { id: 3, title: "SOUR", artist: "Olivia Rodrigo", cover: "https://ui-avatars.com/api/?name=SOUR&background=673ab7&color=fff&size=200" },
    { id: 4, title: "Planet Her", artist: "Doja Cat", cover: "https://ui-avatars.com/api/?name=Planet+Her&background=ff9800&color=fff&size=200" },
    { id: 5, title: "Montero", artist: "Lil Nas X", cover: "https://ui-avatars.com/api/?name=Montero&background=3f51b5&color=fff&size=200" },
];

export default function TrendingSection() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Trending Now</h2>
                <button className="text-sm font-medium text-muted-foreground hover:text-white transition-colors">See all</button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                {trendingAlbums.map((album) => (
                    <div key={album.id} className="group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-colors duration-300 cursor-pointer">
                        <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg">
                            <Image
                                src={album.cover}
                                alt={album.title}
                                width={200}
                                height={200}
                                className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
                            />
                            <button className="absolute bottom-2 right-2 h-12 w-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 hover:scale-105 hover:bg-green-400">
                                <Play className="h-6 w-6 text-black fill-black ml-1" />
                            </button>
                        </div>
                        <h3 className="font-bold text-white truncate">{album.title}</h3>
                        <p className="text-sm text-[#a7a7a7]">{album.artist}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
