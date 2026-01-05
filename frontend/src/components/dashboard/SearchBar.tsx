"use client"

import { Search } from "lucide-react";
import { Input } from "@/components/ui/input"; // We need to create this or use Shadcn input directly

export default function SearchBar() {
    return (
        <div className="relative max-w-2xl mx-auto mb-12 group">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative flex items-center">
                <Search className="absolute left-4 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input
                    type="text"
                    placeholder="What do you want to listen to?"
                    className="w-full h-14 pl-12 pr-6 rounded-full bg-white/5 border border-white/10 text-lg placeholder:text-muted-foreground/70 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:bg-black/80 transition-all shadow-xl"
                />
            </div>
        </div>
    );
}
