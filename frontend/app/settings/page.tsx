"use client"

import { useState, useEffect } from "react";
import { User, Volume2, Bell, Info, ArrowLeft, Loader2, Camera } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Settings {
    // User Profile (Backend)
    displayName: string;
    avatarUrl: string;

    // Client Preferences (LocalStorage)
    audioQuality: 'low' | 'normal' | 'high';
    crossfade: boolean;
    notifyNewReleases: boolean;
    notifyRecommendations: boolean;
}

const SETTINGS_KEY = 'music-discovery-settings';

const defaultSettings: Settings = {
    displayName: '',
    avatarUrl: '',
    audioQuality: 'high',
    crossfade: true,
    notifyNewReleases: true,
    notifyRecommendations: true,
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function SettingsPage() {
    const { user, token, refreshUser, isLoading: authLoading } = useAuth();
    const router = useRouter();
    const [settings, setSettings] = useState<Settings>(defaultSettings);
    const [saved, setSaved] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState("");

    // Load initial settings
    useEffect(() => {
        // Load client prefs
        const stored = localStorage.getItem(SETTINGS_KEY);
        let clientPrefs = {};
        if (stored) {
            try {
                clientPrefs = JSON.parse(stored);
            } catch (e) {
                console.error('Failed to parse settings:', e);
            }
        }

        // Combine with user data if available
        if (user) {
            setSettings(prev => ({
                ...prev,
                ...clientPrefs,
                displayName: user.display_name || user.username || "",
                avatarUrl: user.avatar_url || "",
            }));
        } else if (!authLoading) {
            // Not logged in -> redirect
            router.push("/login");
        }
    }, [user, authLoading, router]);

    const handleSave = async () => {
        setIsSaving(true);
        setError("");

        try {
            // 1. Save Profile to Backend
            if (token) {
                const response = await fetch(`${API_URL}/auth/me`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        display_name: settings.displayName,
                        avatar_url: settings.avatarUrl
                    })
                });

                if (!response.ok) {
                    throw new Error("Failed to update profile");
                }

                // Refresh global user state
                await refreshUser();
            }

            // 2. Save Client Prefs to LocalStorage
            const clientPrefs = {
                audioQuality: settings.audioQuality,
                crossfade: settings.crossfade,
                notifyNewReleases: settings.notifyNewReleases,
                notifyRecommendations: settings.notifyRecommendations
            };
            localStorage.setItem(SETTINGS_KEY, JSON.stringify(clientPrefs));

            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
        } catch (err: any) {
            setError(err.message || "Failed to save settings");
        } finally {
            setIsSaving(false);
        }
    };

    if (authLoading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black">
                <Loader2 className="h-8 w-8 animate-spin text-green-500" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white selection:bg-primary/30">
            {/* Header */}
            <div className="border-b border-white/5 bg-black/40 backdrop-blur-md sticky top-0 z-10">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
                        <ArrowLeft className="h-5 w-5" />
                        <span>Back to Dashboard</span>
                    </Link>
                    <span className="font-bold text-lg">Settings</span>
                </div>
            </div>

            <main className="container mx-auto px-4 py-8 max-w-4xl">

                {/* Account Section */}
                <section className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <User className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold">Profile</h2>
                    </div>
                    <div className="bg-[#181818] rounded-xl p-6 space-y-6">
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        <div className="flex flex-col md:flex-row gap-6">
                            {/* Avatar Preview */}
                            <div className="flex flex-col items-center gap-2">
                                <div className="h-24 w-24 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center overflow-hidden border-2 border-white/10">
                                    {settings.avatarUrl ? (
                                        <img src={settings.avatarUrl} alt="Avatar" className="h-full w-full object-cover" />
                                    ) : (
                                        <span className="text-3xl font-bold text-black">
                                            {(settings.displayName || user.username).charAt(0).toUpperCase()}
                                        </span>
                                    )}
                                </div>
                                <span className="text-xs text-muted-foreground">Preview</span>
                            </div>

                            <div className="flex-1 space-y-4">
                                <div>
                                    <label className="block text-sm text-muted-foreground mb-2">Display Name</label>
                                    <input
                                        type="text"
                                        value={settings.displayName}
                                        onChange={(e) => setSettings({ ...settings, displayName: e.target.value })}
                                        className="w-full bg-[#282828] border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary text-white"
                                        placeholder="Enter your name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-muted-foreground mb-2">Avatar URL</label>
                                    <div className="relative">
                                        <Camera className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                                        <input
                                            type="url"
                                            value={settings.avatarUrl}
                                            onChange={(e) => setSettings({ ...settings, avatarUrl: e.target.value })}
                                            className="w-full bg-[#282828] border border-white/10 rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary text-white"
                                            placeholder="https://example.com/avatar.jpg"
                                        />
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">Link to an image file for your profile picture.</p>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/5">
                            <div>
                                <label className="block text-sm text-muted-foreground mb-2">Username (Read-only)</label>
                                <input
                                    type="text"
                                    value={user.username}
                                    readOnly
                                    className="w-full bg-[#202020] border border-white/5 rounded-lg px-4 py-2 text-gray-400 cursor-not-allowed"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-muted-foreground mb-2">Email (Read-only)</label>
                                <input
                                    type="email"
                                    value={user.email}
                                    readOnly
                                    className="w-full bg-[#202020] border border-white/5 rounded-lg px-4 py-2 text-gray-400 cursor-not-allowed"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* Playback Section */}
                <section className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <Volume2 className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold">Playback</h2>
                    </div>
                    <div className="bg-[#181818] rounded-xl p-6 space-y-4">
                        <div>
                            <label className="block text-sm text-muted-foreground mb-2">Audio Quality</label>
                            <select
                                value={settings.audioQuality}
                                onChange={(e) => setSettings({ ...settings, audioQuality: e.target.value as any })}
                                className="w-full bg-[#282828] border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary text-white"
                            >
                                <option value="low">Low (96 kbps)</option>
                                <option value="normal">Normal (160 kbps)</option>
                                <option value="high">High (320 kbps)</option>
                            </select>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Crossfade</p>
                                <p className="text-sm text-muted-foreground">Seamless transitions between tracks</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, crossfade: !settings.crossfade })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.crossfade ? 'bg-primary' : 'bg-[#282828]'
                                    }`}
                            >
                                <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${settings.crossfade ? 'translate-x-6' : ''
                                    }`} />
                            </button>
                        </div>
                    </div>
                </section>

                {/* Notifications Section */}
                <section className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <Bell className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold">Notifications</h2>
                    </div>
                    <div className="bg-[#181818] rounded-xl p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">New Releases</p>
                                <p className="text-sm text-muted-foreground">Get notified about new music</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, notifyNewReleases: !settings.notifyNewReleases })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.notifyNewReleases ? 'bg-primary' : 'bg-[#282828]'
                                    }`}
                            >
                                <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${settings.notifyNewReleases ? 'translate-x-6' : ''
                                    }`} />
                            </button>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Recommendations</p>
                                <p className="text-sm text-muted-foreground">Personalized music suggestions</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, notifyRecommendations: !settings.notifyRecommendations })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.notifyRecommendations ? 'bg-primary' : 'bg-[#282828]'
                                    }`}
                            >
                                <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${settings.notifyRecommendations ? 'translate-x-6' : ''
                                    }`} />
                            </button>
                        </div>
                    </div>
                </section>

                {/* About Section */}
                <section className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <Info className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold">About</h2>
                    </div>
                    <div className="bg-[#181818] rounded-xl p-6 space-y-2 text-sm text-muted-foreground">
                        <p>Version 1.0.0</p>
                        <p>© 2026 SonicStream</p>
                    </div>
                </section>

                {/* Save Button */}
                <div className="flex items-center gap-4 pb-8">
                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="px-8 py-3 bg-primary text-black rounded-full font-bold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isSaving && <Loader2 className="h-4 w-4 animate-spin" />}
                        {isSaving ? "Saving..." : "Save Changes"}
                    </button>
                    {saved && (
                        <span className="text-primary font-medium animate-in fade-in slide-in-from-left-2">✓ Settings saved</span>
                    )}
                </div>
            </main>
        </div>
    );
}
