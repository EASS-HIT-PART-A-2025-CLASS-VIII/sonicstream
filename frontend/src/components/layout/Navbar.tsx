"use client"

import Link from "next/link";
import { cn } from "@/lib/utils";
import { Loader2, User, LogOut, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/AuthContext";
import { useState, useRef, useEffect } from "react";

export default function Navbar() {
    const { user, isLoading, logout } = useAuth();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/40 backdrop-blur-md">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2 group">
                    <div className="h-8 w-8 bg-gradient-to-tr from-green-500 to-emerald-300 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Loader2 className="h-5 w-5 text-black animate-spin-slow" />
                    </div>
                    <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        SonicStream
                    </span>
                </Link>

                {/* Navigation */}
                <div className="hidden md:flex items-center gap-6 text-sm font-medium text-muted-foreground">
                    <Link href="#" className="hover:text-primary transition-colors">Features</Link>
                    <Link href="#" className="hover:text-primary transition-colors">Pricing</Link>
                    <Link href="#" className="hover:text-primary transition-colors">Careers</Link>
                </div>

                {/* Auth Section */}
                <div className="flex items-center gap-4">
                    {isLoading ? (
                        <div className="h-8 w-8 rounded-full bg-white/10 animate-pulse" />
                    ) : user ? (
                        // Logged in state
                        <div className="relative" ref={dropdownRef}>
                            <button
                                onClick={() => setDropdownOpen(!dropdownOpen)}
                                className="flex items-center gap-2 p-1 pr-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                <div className="h-8 w-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center">
                                    {user.avatar_url ? (
                                        <img
                                            src={user.avatar_url}
                                            alt={user.display_name || user.username}
                                            className="h-full w-full rounded-full object-cover"
                                        />
                                    ) : (
                                        <span className="text-sm font-bold text-black">
                                            {(user.display_name || user.username).charAt(0).toUpperCase()}
                                        </span>
                                    )}
                                </div>
                                <span className="text-sm font-medium hidden sm:block">
                                    {user.display_name || user.username}
                                </span>
                                <ChevronDown className={cn(
                                    "h-4 w-4 text-gray-400 transition-transform",
                                    dropdownOpen && "rotate-180"
                                )} />
                            </button>

                            {/* Dropdown Menu */}
                            {dropdownOpen && (
                                <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-white/10 rounded-lg shadow-xl overflow-hidden">
                                    <Link
                                        href="/profile"
                                        className="flex items-center gap-2 px-4 py-3 text-sm hover:bg-white/5 transition-colors"
                                        onClick={() => setDropdownOpen(false)}
                                    >
                                        <User className="h-4 w-4 text-gray-400" />
                                        <span>Profile</span>
                                    </Link>
                                    <button
                                        onClick={() => {
                                            logout();
                                            setDropdownOpen(false);
                                        }}
                                        className="flex items-center gap-2 px-4 py-3 text-sm hover:bg-white/5 transition-colors w-full text-left text-red-400"
                                    >
                                        <LogOut className="h-4 w-4" />
                                        <span>Log Out</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        // Logged out state
                        <>
                            <Link href="/login" className="text-sm font-medium hover:text-white transition-colors hidden sm:block">
                                Log in
                            </Link>
                            <Link href="/register">
                                <Button className="bg-primary text-black hover:bg-primary/90 font-bold rounded-full px-6">
                                    Sign Up Free
                                </Button>
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
