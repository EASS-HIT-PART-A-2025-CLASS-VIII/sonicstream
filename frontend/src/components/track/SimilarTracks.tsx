"use client"

import { Track } from "@/lib/mockData";
import TrackCard from "@/components/discovery/TrackCard";

interface SimilarTracksProps {
    tracks: Track[];
}

export default function SimilarTracks({ tracks }: SimilarTracksProps) {
    if (tracks.length === 0) return null;

    return (
        <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">You Might Also Like</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                {tracks.map(track => (
                    <TrackCard key={track.id} track={track} />
                ))}
            </div>
        </div>
    );
}
