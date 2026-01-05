"use client"

import Link from "next/link";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react"; // Using Loader icon as logo placeholder
import { Button } from "@/components/ui/button";

export default function Navbar() {
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

                {/* CTA */}
                <div className="flex items-center gap-4">
                    <Link href="/login" className="text-sm font-medium hover:text-white transition-colors hidden sm:block">
                        Log in
                    </Link>
                    <Button className="bg-primary text-black hover:bg-primary/90 font-bold rounded-full px-6">
                        Sign Up Free
                    </Button>
                </div>
            </div>
        </nav>
    );
}
