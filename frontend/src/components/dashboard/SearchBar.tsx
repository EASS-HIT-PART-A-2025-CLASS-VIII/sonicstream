"use client"

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import api, { Track } from "@/lib/api";
import Link from "next/link";

export default function SearchBar() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<Track[]>([]);
    const [loading, setLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const router = useRouter();

    const handleSearch = async (searchQuery: string) => {
        setQuery(searchQuery);

        if (searchQuery.length < 2) {
            setResults([]);
            setShowResults(false);
            return;
        }

        setLoading(true);
        try {
            const response = await api.searchTracks(searchQuery, 0, 5);
            setResults(response.tracks);
            setShowResults(true);
        } catch (error) {
            console.error("Search failed:", error);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.length >= 2) {
            setShowResults(false);
            router.push(`/discovery?search=${encodeURIComponent(query)}`);
        }
    };

    return (
        <div className="relative max-w-2xl mx-auto mb-12 group">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <form onSubmit={handleSubmit} className="relative">
                <div className="relative flex items-center">
                    {loading ? (
                        <Loader2 className="absolute left-4 h-5 w-5 text-muted-foreground animate-spin" />
                    ) : (
                        <Search className="absolute left-4 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    )}
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => handleSearch(e.target.value)}
                        onFocus={() => query.length >= 2 && setShowResults(true)}
                        onBlur={() => setTimeout(() => setShowResults(false), 200)}
                        placeholder="What do you want to listen to?"
                        className="w-full h-14 pl-12 pr-6 rounded-full bg-white/5 border border-white/10 text-lg placeholder:text-muted-foreground/70 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:bg-black/80 transition-all shadow-xl"
                    />
                </div>
            </form>

            {/* Search Results Dropdown */}
            {showResults && results.length > 0 && (
                <div className="absolute top-full mt-2 w-full bg-[#181818] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50">
                    {results.map((track) => (
                        <Link
                            key={track.id}
                            href={`/track/${track.id}`}
                            className="flex items-center gap-4 p-4 hover:bg-white/5 transition-colors"
                        >
                            <div className="h-12 w-12 bg-[#282828] rounded flex items-center justify-center text-xs font-bold">
                                {track.name.charAt(0)}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="font-medium truncate">{track.name}</p>
                                <p className="text-sm text-muted-foreground truncate">{track.artist}</p>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
