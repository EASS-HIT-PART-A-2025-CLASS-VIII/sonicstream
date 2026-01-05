"use client"

import { useFavorites } from "@/lib/favorites";
import TrackCard from "@/components/discovery/TrackCard";
import { Heart } from "lucide-react";

export default function FavoritesPage() {
    const { favorites, isLoaded } = useFavorites();

    if (!isLoaded) {
        return (
            <div className="py-6">
                <h1 className="text-3xl md:text-4xl font-bold mb-8">Your Library</h1>
                <div className="flex justify-center items-center py-20">
                    <div className="animate-pulse text-muted-foreground">Loading...</div>
                </div>
            </div>
        );
    }

    if (favorites.length === 0) {
        return (
            <div className="py-6">
                <h1 className="text-3xl md:text-4xl font-bold mb-8">Your Library</h1>
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <div className="h-24 w-24 rounded-full bg-white/5 flex items-center justify-center mb-6">
                        <Heart className="h-12 w-12 text-muted-foreground" />
                    </div>
                    <h2 className="text-2xl font-bold mb-2">No favorites yet</h2>
                    <p className="text-muted-foreground max-w-md mb-8">
                        Tracks you like will appear here. Start exploring and tap the heart icon on any track to save it.
                    </p>
                    <a
                        href="/discovery"
                        className="px-6 py-3 bg-primary text-black rounded-full font-semibold hover:bg-primary/90 transition-colors"
                    >
                        Discover Music
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="py-6">
            <div className="mb-8">
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Your Library</h1>
                <p className="text-muted-foreground">{favorites.length} liked tracks</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {favorites.map(track => (
                    <TrackCard key={track.id} track={track} />
                ))}
            </div>
        </div>
    );
}
