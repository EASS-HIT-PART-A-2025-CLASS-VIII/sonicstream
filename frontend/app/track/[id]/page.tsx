"use client"

import { useState, useEffect } from "react";
import { notFound } from "next/navigation";
import Image from "next/image";
import api, { Track, SimilarTrack } from "@/lib/api";
import AudioFeaturesChart from "@/components/track/AudioFeaturesChart";
import SimilarTracks from "@/components/track/SimilarTracks";
import { Play, Heart, MoreHorizontal, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TrackPage({ params }: { params: { id: string } }) {
    const [track, setTrack] = useState<Track | null>(null);
    const [similarTracks, setSimilarTracks] = useState<SimilarTrack[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadTrack() {
            try {
                setLoading(true);
                const [trackData, similar] = await Promise.all([
                    api.getTrack(params.id),
                    api.getSimilarTracks(params.id, 10)
                ]);
                setTrack(trackData);
                setSimilarTracks(similar);
                setError(null);
            } catch (err) {
                setError("Failed to load track");
            } finally {
                setLoading(false);
            }
        }
        loadTrack();
    }, [params.id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (error || !track) {
        return (
            <div className="text-center py-20">
                <h2 className="text-2xl font-bold mb-2">Track not found</h2>
                <p className="text-muted-foreground">{error || "The track you're looking for doesn't exist."}</p>
            </div>
        );
    }

    const duration = track.duration_ms ? Math.floor(track.duration_ms / 1000) : 0;
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;

    const audioFeatures = {
        danceability: track.danceability || 0,
        energy: track.energy || 0,
        valence: track.valence || 0,
        tempo: track.tempo || 120,
        acousticness: track.acousticness || 0,
    };

    return (
        <div className="py-6">
            {/* Hero Section */}
            <div className="flex flex-col md:flex-row gap-8 mb-12">
                <div className="relative w-full md:w-80 aspect-square rounded-xl overflow-hidden shadow-2xl">
                    <Image
                        src={track.cover_url || `https://ui-avatars.com/api/?name=${track.artist}&background=random&color=fff&size=300`}
                        alt={track.name}
                        fill
                        className="object-cover"
                        priority
                    />
                </div>

                <div className="flex flex-col justify-end">
                    <p className="text-sm font-semibold text-muted-foreground mb-2">SONG</p>
                    <h1 className="text-4xl md:text-6xl font-black mb-6 leading-tight">{track.name}</h1>
                    <div className="flex items-center gap-2 text-sm flex-wrap">
                        <span className="font-semibold">{track.artist}</span>
                        {track.album && (
                            <>
                                <span className="text-muted-foreground">•</span>
                                <span className="text-muted-foreground">{track.album}</span>
                            </>
                        )}
                        {duration > 0 && (
                            <>
                                <span className="text-muted-foreground">•</span>
                                <span className="text-muted-foreground">{minutes}:{seconds.toString().padStart(2, '0')}</span>
                            </>
                        )}
                        {track.genre && (
                            <>
                                <span className="text-muted-foreground">•</span>
                                <span className="text-primary">{track.genre}</span>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4 mb-12">
                <Button size="lg" className="h-14 px-8 rounded-full bg-primary text-black hover:bg-primary/90 text-lg font-bold">
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

            {/* Audio Features */}
            <div className="mb-12">
                <AudioFeaturesChart features={audioFeatures} />
            </div>

            {/* Feature Details */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Danceability</p>
                    <p className="text-2xl font-bold">{Math.round((track.danceability || 0) * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Energy</p>
                    <p className="text-2xl font-bold">{Math.round((track.energy || 0) * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Valence</p>
                    <p className="text-2xl font-bold">{Math.round((track.valence || 0) * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Tempo</p>
                    <p className="text-2xl font-bold">{Math.round(track.tempo || 0)} BPM</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Acousticness</p>
                    <p className="text-2xl font-bold">{Math.round((track.acousticness || 0) * 100)}%</p>
                </div>
            </div>

            {/* Similar Tracks */}
            {similarTracks.length > 0 && (
                <SimilarTracks tracks={similarTracks as any} />
            )}
        </div>
    );
}
