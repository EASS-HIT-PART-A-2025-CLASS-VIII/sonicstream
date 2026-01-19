"use client";

import { useState, useEffect, useCallback } from "react";
import { Disc3, Loader2, AlertCircle, RefreshCw, Sparkles, Search } from "lucide-react";
import AlbumCard from "@/components/discovery/AlbumCard";
import { Album, SimilarAlbum } from "@/lib/api";
import { useDebounce } from "@/hooks/useDebounce";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function AlbumMatchPage() {
    const [allAlbums, setAllAlbums] = useState<Album[]>([]);
    const [selectedAlbumId, setSelectedAlbumId] = useState<string | null>(null);
    const [recommendations, setRecommendations] = useState<SimilarAlbum[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingAlbums, setIsLoadingAlbums] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [step, setStep] = useState<"select" | "results">("select");
    const [searchQuery, setSearchQuery] = useState("");
    const debouncedQuery = useDebounce(searchQuery, 300);

    // Fetch default albums
    const fetchDefaultAlbums = () => {
        setIsLoadingAlbums(true);
        fetch(`${API_URL}/albums?page_size=40`)
            .then(res => res.json())
            .then(data => {
                const albums = data.albums || [];
                setAllAlbums(albums);
                setIsLoadingAlbums(false);
                setError(null);
            })
            .catch(err => {
                console.error("Failed to load albums:", err);
                setError("Failed to load albums. Make sure the backend is running.");
                setIsLoadingAlbums(false);
            });
    };

    // Initial load
    useEffect(() => {
        fetchDefaultAlbums();
    }, []);

    // Search effect
    useEffect(() => {
        if (debouncedQuery.length >= 2) {
            setIsLoadingAlbums(true);
            fetch(`${API_URL}/albums/search?q=${encodeURIComponent(debouncedQuery)}&page_size=40`)
                .then(res => res.json())
                .then(data => {
                    setAllAlbums(data.albums || []);
                    setError(null);
                })
                .catch(err => {
                    console.error("Search failed:", err);
                    setError("Search failed. Please try again.");
                })
                .finally(() => setIsLoadingAlbums(false));
        } else if (debouncedQuery.length === 0) {
            fetchDefaultAlbums();
        }
    }, [debouncedQuery]);

    const selectAlbum = (albumId: string) => {
        setSelectedAlbumId(prev => prev === albumId ? null : albumId);
    };

    const getRecommendations = async () => {
        if (!selectedAlbumId) return;

        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/albums/recommend`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    album_id: selectedAlbumId,
                    limit: 12
                })
            });
            const data = await response.json();
            setRecommendations(data || []);
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
        setSelectedAlbumId(null);
        setSearchQuery("");
        fetchDefaultAlbums();
    };

    const selectedAlbum = allAlbums.find(a => a.id === selectedAlbumId);

    return (
        <div className="py-2 space-y-10">
            {/* Header / Hero Section */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent p-8 md:p-12 border border-white/5 shadow-2xl">
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[100px] -mr-32 -mt-32 animate-pulse" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] -ml-32 -mb-32 animate-pulse" />
                
                <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <div className="space-y-4 max-w-2xl">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs font-bold text-primary tracking-wider uppercase">
                            <Sparkles className="h-3.5 w-3.5" />
                            AI-Powered Discovery
                        </div>
                        <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-tight">
                            Album <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">Match</span>
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
                            {step === "select"
                                ? "Select an album from the library or search for one to find its musical soulmates using our neural audio analysis."
                                : `Musical soulmates discovered for "${selectedAlbum?.name}". Based on 9 combined acoustic and musical characteristics.`}
                        </p>
                    </div>

                    <div className="flex-shrink-0">
                        {step === "select" ? (
                            selectedAlbumId ? (
                                <button
                                    onClick={getRecommendations}
                                    disabled={isLoading}
                                    className="h-14 px-8 bg-primary hover:scale-105 active:scale-95 text-black font-black rounded-2xl transition-all flex items-center gap-3 disabled:opacity-50 shadow-2xl shadow-primary/30 group"
                                >
                                    {isLoading ? (
                                        <Loader2 className="h-6 w-6 animate-spin" />
                                    ) : (
                                        <Sparkles className="h-6 w-6 group-hover:rotate-12 transition-transform" />
                                    )}
                                    <span className="text-lg">Find Matches</span>
                                </button>
                            ) : (
                                <div className="hidden md:block h-14 px-8 border border-white/10 text-white/40 font-bold rounded-2xl flex items-center gap-3 opacity-50 cursor-not-allowed">
                                    <Sparkles className="h-6 w-6" />
                                    <span className="text-lg">Select an Album</span>
                                </div>
                            )
                        ) : (
                            <button
                                onClick={resetSelection}
                                className="h-14 px-8 border border-white/10 hover:bg-white/5 active:scale-95 text-white font-bold rounded-2xl transition-all flex items-center gap-3 glass"
                            >
                                <RefreshCw className="h-5 w-5" />
                                <span className="text-lg">Start New Search</span>
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Search Controls */}
            {step === "select" && (
                <div className="relative group max-w-3xl">
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-2xl blur opacity-25 group-focus-within:opacity-100 transition duration-1000 group-focus-within:duration-200"></div>
                    <div className="relative flex items-center bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                        <Search className="absolute left-6 h-6 w-6 text-muted-foreground group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search by album title, artist, or genre..."
                            className="w-full h-16 pl-16 pr-6 bg-transparent text-xl placeholder:text-muted-foreground/50 focus:outline-none"
                        />
                         {isLoadingAlbums && (
                            <div className="px-6 border-l border-white/5">
                                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {step === "select" ? (
                // Album Selection Grid
                <>
                    {isLoadingAlbums ? (
                        <div className="flex justify-center items-center py-12">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                            {allAlbums.map(album => (
                                <AlbumCard
                                    key={album.id}
                                    album={album}
                                    isSelected={selectedAlbumId === album.id}
                                    onClick={() => selectAlbum(album.id)}
                                />
                            ))}
                        </div>
                    )}

                    {!isLoadingAlbums && allAlbums.length === 0 && !error && (
                        <div className="text-center py-12 text-muted-foreground">
                            No albums found.
                        </div>
                    )}
                </>
            ) : (
                // Recommendations Results
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {recommendations.map((album) => (
                        <AlbumCard key={album.id} album={album} />
                    ))}
                </div>
            )}
        </div>
    );
}
