"use client";

import { useState, useEffect, useCallback } from "react";
import { Sparkles, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import TrackCard from "@/components/discovery/TrackCard";
import SearchBar from "@/components/dashboard/SearchBar";
import { Track } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function RecommendationsPage() {
    const [allTracks, setAllTracks] = useState<Track[]>([]);
    const [selectedTrackIds, setSelectedTrackIds] = useState<Set<string>>(new Set());
    const [recommendations, setRecommendations] = useState<Track[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingTracks, setIsLoadingTracks] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [step, setStep] = useState<"select" | "results">("select");

    // Fetch default tracks
    const fetchDefaultTracks = () => {
        setIsLoadingTracks(true);
        fetch(`${API_URL}/recommendations/tracks?page_size=50`)
            .then(res => res.json())
            .then(data => {
                const tracks = data.tracks || [];
                setAllTracks(tracks);
                setIsLoadingTracks(false);
                setError(null);
            })
            .catch(err => {
                console.error("Failed to load tracks:", err);
                setError("Failed to load tracks. Make sure the backend is running.");
                setIsLoadingTracks(false);
            });
    };

    // Fetch tracks for selection (initial load)
    useEffect(() => {
        fetchDefaultTracks();
    }, []);

    const handleSearch = useCallback(async (query: string) => {
        setIsLoadingTracks(true);
        try {
            // Use the API client for search
            const data = await import("@/lib/api").then(m => m.default.searchTracks(query, 0, 50));
            setAllTracks(data.tracks || []);
            setError(null);
        } catch (err) {
            console.error("Search failed:", err);
            setError("Search failed. Please try again.");
        } finally {
            setIsLoadingTracks(false);
        }
    }, []);

    const toggleTrack = (trackId: string) => {
        setSelectedTrackIds(prev => {
            const next = new Set(prev);
            if (next.has(trackId)) {
                next.delete(trackId);
            } else {
                next.add(trackId);
            }
            return next;
        });
    };

    const getRecommendations = async () => {
        if (selectedTrackIds.size === 0) return;

        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/recommendations/tracks`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    track_ids: Array.from(selectedTrackIds),
                    limit: 12
                })
            });
            const data = await response.json();
            setRecommendations(data.tracks || []);
            setStep("results");
            setError(null);
        } catch (err) {
            console.error("Failed to get recommendations:", err);
            setError("Failed to get recommendations. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const resetSelection = () => {
        setStep("select");
        setRecommendations([]);
        setSelectedTrackIds(new Set());
        fetchDefaultTracks(); // Reset track list to default
    };

    return (
        <div className="py-6">
            <div className="mb-8">
                <SearchBar onSearch={handleSearch} />
                <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold mb-2">For You</h1>
                        <p className="text-muted-foreground">
                            {step === "select"
                                ? "Select songs you like to get personalized recommendations"
                                : "AI-curated playlist based on your vibes"}
                        </p>
                    </div>

                    {step === "select" && selectedTrackIds.size > 0 && (
                        <button
                            onClick={getRecommendations}
                            disabled={isLoading}
                            className="h-12 px-6 bg-primary hover:bg-primary/90 text-black font-bold rounded-full transition-colors flex items-center gap-2 disabled:opacity-50 shadow-lg shadow-primary/20"
                        >
                            {isLoading ? (
                                <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                                <Sparkles className="h-5 w-5" />
                            )}
                            Generate Mix ({selectedTrackIds.size})
                        </button>
                    )}

                    {step === "results" && (
                        <button
                            onClick={resetSelection}
                            className="h-12 px-6 border border-white/10 hover:bg-white/5 text-white font-semibold rounded-full transition-colors flex items-center gap-2"
                        >
                            <RefreshCw className="h-4 w-4" />
                            Start Over
                        </button>
                    )}
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {step === "select" ? (
                // Track Selection Grid
                <>
                    {isLoadingTracks ? (
                        <div className="flex justify-center items-center py-12">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                            {allTracks.map(track => {
                                const isSelected = selectedTrackIds.has(track.id);
                                return (
                                    <div
                                        key={track.id}
                                        onClick={() => toggleTrack(track.id)}
                                        className={`relative transition-transform duration-200 ${isSelected ? 'scale-95 ring-2 ring-primary rounded-xl' : ''}`}
                                    >
                                        {/* Selection Overlay */}
                                        <div className={`absolute inset-0 z-10 bg-black/40 rounded-xl flex items-center justify-center transition-opacity border-2 border-primary ${isSelected ? 'opacity-100' : 'opacity-0 hover:opacity-100 cursor-pointer'}`}>
                                            <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${isSelected ? 'bg-primary border-primary' : 'border-white'}`}>
                                                {isSelected && <Sparkles className="h-4 w-4 text-black" />}
                                            </div>
                                        </div>

                                        {/* Reuse TrackCard for visuals */}
                                        <div className="pointer-events-none">
                                            <TrackCard track={track} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {!isLoadingTracks && allTracks.length === 0 && !error && (
                        <div className="text-center py-12 text-muted-foreground">
                            No tracks found.
                        </div>
                    )}
                </>
            ) : (
                // Recommendations Results
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {recommendations.map((track) => (
                        <TrackCard key={track.id} track={track} />
                    ))}
                </div>
            )}
        </div>
    );
}
