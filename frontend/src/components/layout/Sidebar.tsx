"use client"

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, Compass, Heart, Settings, Loader2, User, LogOut, ChevronUp, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { useState, useRef, useEffect } from "react";

const navItems = [
    { icon: Home, label: "Home", href: "/dashboard" },
    { icon: Compass, label: "Discovery", href: "/discovery" },
    { icon: Sparkles, label: "Album Match", href: "/album-match" },
    { icon: Heart, label: "Favorites", href: "/favorites" },
    { icon: Settings, label: "Settings", href: "/settings" },
];

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
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

    const handleLogout = () => {
        logout();
        setDropdownOpen(false);
        router.push("/");
    };

    return (
        <aside className="hidden md:flex flex-col w-64 h-screen fixed left-0 top-0 border-r border-white/5 bg-black/50 backdrop-blur-xl p-6">
            {/* Logo */}
            <div className="flex items-center gap-2 mb-10 px-2">
                <div className="h-8 w-8 bg-gradient-to-tr from-green-500 to-emerald-300 rounded-full flex items-center justify-center">
                    <Loader2 className="h-5 w-5 text-black animate-spin-slow" />
                </div>
                <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    SonicStream
                </span>
            </div>

            {/* Nav Links */}
            <nav className="flex flex-col gap-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group",
                                isActive
                                    ? "bg-primary/10 text-primary font-semibold"
                                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                            )}
                        >
                            <item.icon className={cn("h-5 w-5", isActive && "text-primary")} />
                            <span>{item.label}</span>
                            {isActive && (
                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(30,215,96,0.5)]" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* User Info (Bottom) */}
            <div className="mt-auto pt-6 border-t border-white/5" ref={dropdownRef}>
                {isLoading ? (
                    <div className="flex items-center gap-3 px-2">
                        <div className="h-10 w-10 rounded-full bg-white/10 animate-pulse" />
                        <div className="flex flex-col gap-1">
                            <div className="h-4 w-20 bg-white/10 rounded animate-pulse" />
                            <div className="h-3 w-16 bg-white/10 rounded animate-pulse" />
                        </div>
                    </div>
                ) : user ? (
                    <div className="relative">
                        {/* Dropdown Menu (appears above) */}
                        {dropdownOpen && (
                            <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-900 border border-white/10 rounded-xl shadow-xl overflow-hidden">
                                <Link
                                    href="/profile"
                                    className="flex items-center gap-3 px-4 py-3 text-sm hover:bg-white/5 transition-colors"
                                    onClick={() => setDropdownOpen(false)}
                                >
                                    <User className="h-4 w-4 text-gray-400" />
                                    <span>Profile</span>
                                </Link>
                                <Link
                                    href="/favorites"
                                    className="flex items-center gap-3 px-4 py-3 text-sm hover:bg-white/5 transition-colors"
                                    onClick={() => setDropdownOpen(false)}
                                >
                                    <Heart className="h-4 w-4 text-gray-400" />
                                    <span>My Favorites</span>
                                </Link>
                                <Link
                                    href="/settings"
                                    className="flex items-center gap-3 px-4 py-3 text-sm hover:bg-white/5 transition-colors"
                                    onClick={() => setDropdownOpen(false)}
                                >
                                    <Settings className="h-4 w-4 text-gray-400" />
                                    <span>Settings</span>
                                </Link>
                                <button
                                    onClick={handleLogout}
                                    className="flex items-center gap-3 px-4 py-3 text-sm hover:bg-white/5 transition-colors w-full text-left text-red-400 border-t border-white/5"
                                >
                                    <LogOut className="h-4 w-4" />
                                    <span>Log Out</span>
                                </button>
                            </div>
                        )}

                        {/* User Button */}
                        <button
                            onClick={() => setDropdownOpen(!dropdownOpen)}
                            className="flex items-center gap-3 px-2 py-2 w-full rounded-xl hover:bg-white/5 transition-colors"
                        >
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-sm font-bold text-black">
                                {(user.display_name || user.username).charAt(0).toUpperCase()}
                            </div>
                            <div className="flex flex-col text-left flex-1 min-w-0">
                                <span className="text-sm font-medium truncate">
                                    {user.display_name || user.username}
                                </span>
                                <span className="text-xs text-muted-foreground truncate">
                                    {user.email}
                                </span>
                            </div>
                            <ChevronUp className={cn(
                                "h-4 w-4 text-gray-400 transition-transform flex-shrink-0",
                                dropdownOpen && "rotate-180"
                            )} />
                        </button>
                    </div>
                ) : (
                    <Link
                        href="/login"
                        className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-black font-bold rounded-xl hover:opacity-90 transition-opacity"
                    >
                        <User className="h-4 w-4" />
                        <span>Sign In</span>
                    </Link>
                )}
            </div>
        </aside>
    );
}
