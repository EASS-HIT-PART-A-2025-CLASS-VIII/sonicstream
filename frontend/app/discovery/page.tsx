"use client"

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import api, { Track } from "@/lib/api";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";
import TrackCard from "@/components/discovery/TrackCard";
import SearchBar from "@/components/dashboard/SearchBar";
import { Loader2, AlertCircle } from "lucide-react";

function DiscoveryContent() {
    const searchParams = useSearchParams();
    const router = useRouter(); // Import this
    const query = searchParams.get("search");
    const [error, setError] = useState<string | null>(null);

    // Live search handler
    const handleSearch = (newQuery: string) => {
        const params = new URLSearchParams(searchParams);
        if (newQuery) {
            params.set("search", newQuery);
        } else {
            params.delete("search");
        }
        router.replace(`/discovery?${params.toString()}`);
    };

    const fetchTracks = async (page: number): Promise<Track[]> => {
        try {
            let response;
            if (query) {
                response = await api.searchTracks(query, page, 20);
            } else {
                response = await api.getTracks(page, 20);
            }
            setError(null);
            return response.tracks;
        } catch (err) {
            setError("Failed to load tracks. Make sure the backend is running.");
            return [];
        }
    };

    const { items: tracks, loading, hasMore, lastElementRef } = useInfiniteScroll({
        fetchMore: fetchTracks,
        pageSize: 20,
        dependencies: [query] // Reset list when query changes
    });

    return (
        <div className="py-6">
            <div className="mb-8">
                <SearchBar onSearch={handleSearch} />
                <h1 className="text-3xl md:text-4xl font-bold mb-2">
                    {query ? `Results for "${query}"` : "Discover"}
                </h1>
                <p className="text-muted-foreground">
                    {query ? "Found in our library" : "AI-curated tracks from 8 million Spotify songs"}
                </p>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {tracks.map((track, index) => (
                    <div
                        key={track.id}
                        ref={index === tracks.length - 1 ? lastElementRef : null}
                    >
                        <TrackCard track={track} />
                    </div>
                ))}
            </div>

            {loading && (
                <div className="flex justify-center items-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            )}

            {!hasMore && tracks.length > 0 && (
                <div className="text-center py-12 text-muted-foreground">
                    You've reached the end! 🎵
                </div>
            )}

            {!loading && tracks.length === 0 && !error && (
                <div className="text-center py-12 text-muted-foreground">
                    No tracks found. Try refreshing the page.
                </div>
            )}
        </div>
    );
}

export default function DiscoveryPage() {
    return (
        <Suspense fallback={<div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin" /></div>}>
            <DiscoveryContent />
        </Suspense>
    );
}
