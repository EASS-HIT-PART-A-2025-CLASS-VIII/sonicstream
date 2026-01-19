"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, Compass, Heart, User, Sparkles } from "lucide-react";

const navItems = [
    { icon: Home, label: "Home", href: "/dashboard" },
    { icon: Compass, label: "Explore", href: "/discovery" },
    { icon: Sparkles, label: "Match", href: "/album-match" },
    { icon: Heart, label: "Likes", href: "/favorites" },
    { icon: User, label: "Profile", href: "/profile" },
];

export default function MobileNav() {
    const pathname = usePathname();

    return (
        <nav className="md:hidden fixed bottom-0 left-0 w-full bg-black/80 backdrop-blur-xl border-t border-white/10 z-50 pb-safe">
            <div className="flex justify-around items-center h-16 px-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex flex-col items-center justify-center w-full h-full gap-1",
                                isActive ? "text-primary" : "text-muted-foreground"
                            )}
                        >
                            <item.icon className={cn("h-6 w-6 transition-transform", isActive && "scale-110")} />
                            <span className="text-[10px] font-medium">{item.label}</span>
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
