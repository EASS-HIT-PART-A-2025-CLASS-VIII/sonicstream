"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, Compass, Heart, Settings, Loader2 } from "lucide-react";

const navItems = [
    { icon: Home, label: "Home", href: "/dashboard" },
    { icon: Compass, label: "Discovery", href: "/discovery" },
    { icon: Heart, label: "Favorites", href: "/favorites" },
    { icon: Settings, label: "Settings", href: "/settings" },
];

export default function Sidebar() {
    const pathname = usePathname();

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
            <div className="mt-auto pt-6 border-t border-white/5">
                <div className="flex items-center gap-3 px-2">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xs font-bold">
                        JD
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium">John Doe</span>
                        <span className="text-xs text-muted-foreground">Premium Plan</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
