"use client";

import { useAuth } from "@/lib/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Loader2, User, Mail, Calendar, ArrowLeft } from "lucide-react";

export default function ProfilePage() {
    const { user, isLoading, logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login");
        }
    }, [user, isLoading, router]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black">
                <Loader2 className="h-8 w-8 animate-spin text-green-500" />
            </div>
        );
    }

    if (!user) {
        return null;
    }

    const memberSince = new Date(user.created_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    const handleLogout = () => {
        logout();
        router.push("/");
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
            {/* Header */}
            <div className="border-b border-white/5 bg-black/40 backdrop-blur-md">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
                        <ArrowLeft className="h-5 w-5" />
                        <span>Back to Dashboard</span>
                    </Link>
                    <Link href="/" className="flex items-center gap-2">
                        <div className="h-8 w-8 bg-gradient-to-tr from-green-500 to-emerald-300 rounded-full flex items-center justify-center">
                            <Loader2 className="h-5 w-5 text-black" />
                        </div>
                        <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            SonicStream
                        </span>
                    </Link>
                </div>
            </div>

            {/* Profile Content */}
            <div className="container mx-auto px-4 py-12">
                <div className="max-w-2xl mx-auto">
                    {/* Profile Card */}
                    <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8">
                        {/* Avatar & Name */}
                        <div className="flex flex-col items-center mb-8">
                            <div className="h-24 w-24 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mb-4">
                                {user.avatar_url ? (
                                    <img
                                        src={user.avatar_url}
                                        alt={user.display_name || user.username}
                                        className="h-full w-full rounded-full object-cover"
                                    />
                                ) : (
                                    <span className="text-4xl font-bold text-black">
                                        {(user.display_name || user.username).charAt(0).toUpperCase()}
                                    </span>
                                )}
                            </div>
                            <h1 className="text-2xl font-bold">
                                {user.display_name || user.username}
                            </h1>
                            <p className="text-gray-400">@{user.username}</p>
                        </div>

                        {/* Info Grid */}
                        <div className="space-y-4 mb-8">
                            <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
                                <Mail className="h-5 w-5 text-green-500" />
                                <div>
                                    <p className="text-sm text-gray-400">Email</p>
                                    <p className="font-medium">{user.email}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
                                <User className="h-5 w-5 text-green-500" />
                                <div>
                                    <p className="text-sm text-gray-400">Username</p>
                                    <p className="font-medium">@{user.username}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
                                <Calendar className="h-5 w-5 text-green-500" />
                                <div>
                                    <p className="text-sm text-gray-400">Member Since</p>
                                    <p className="font-medium">{memberSince}</p>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col sm:flex-row gap-3">
                            <Button
                                variant="outline"
                                className="flex-1 border-white/10 hover:bg-white/5"
                                onClick={() => router.push("/settings")}
                            >
                                Edit Profile
                            </Button>
                            <Button
                                onClick={handleLogout}
                                variant="destructive"
                                className="flex-1 bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20"
                            >
                                Log Out
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
