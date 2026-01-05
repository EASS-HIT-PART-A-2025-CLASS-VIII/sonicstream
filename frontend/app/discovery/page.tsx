"use client"

import { getDiscoveryTracks, Track } from "@/lib/mockData";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";
import TrackCard from "@/components/discovery/TrackCard";
import { Loader2 } from "lucide-react";

export default function DiscoveryPage() {
    const fetchTracks = async (page: number): Promise<Track[]> => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        return getDiscoveryTracks(page, 20);
    };

    const { items: tracks, loading, hasMore, lastElementRef } = useInfiniteScroll({
        fetchMore: fetchTracks,
        pageSize: 20,
    });

    return (
        <div className="py-6">
            <div className="mb-8">
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Discover</h1>
                <p className="text-muted-foreground">AI-curated tracks just for you</p>
            </div>

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
        </div>
    );
}
