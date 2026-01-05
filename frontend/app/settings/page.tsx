"use client"

import { useState, useEffect } from "react";
import { User, Volume2, Bell, Info } from "lucide-react";

interface Settings {
    username: string;
    email: string;
    audioQuality: 'low' | 'normal' | 'high';
    crossfade: boolean;
    notifyNewReleases: boolean;
    notifyRecommendations: boolean;
}

const SETTINGS_KEY = 'music-discovery-settings';

const defaultSettings: Settings = {
    username: 'Music Lover',
    email: 'user@example.com',
    audioQuality: 'high',
    crossfade: true,
    notifyNewReleases: true,
    notifyRecommendations: true,
};

export default function SettingsPage() {
    const [settings, setSettings] = useState<Settings>(defaultSettings);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem(SETTINGS_KEY);
        if (stored) {
            try {
                setSettings({ ...defaultSettings, ...JSON.parse(stored) });
            } catch (e) {
                console.error('Failed to parse settings:', e);
            }
        }
    }, []);

    const handleSave = () => {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="py-6 max-w-4xl">
            <h1 className="text-3xl md:text-4xl font-bold mb-8">Settings</h1>

            {/* Account Section */}
            <section className="mb-8">
                <div className="flex items-center gap-3 mb-4">
                    <User className="h-5 w-5 text-primary" />
                    <h2 className="text-xl font-bold">Account</h2>
                </div>
                <div className="bg-[#181818] rounded-xl p-6 space-y-4">
                    <div>
                        <label className="block text-sm text-muted-foreground mb-2">Username</label>
                        <input
                            type="text"
                            value={settings.username}
                            onChange={(e) => setSettings({ ...settings, username: e.target.value })}
                            className="w-full bg-[#282828] border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                    </div>
                    <div>
                        <label className="block text-sm text-muted-foreground mb-2">Email</label>
                        <input
                            type="email"
                            value={settings.email}
                            onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                            className="w-full bg-[#282828] border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        />
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
                            className="w-full bg-[#282828] border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
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
                    <div className="pt-2 space-x-4">
                        <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                    </div>
                </div>
            </section>

            {/* Save Button */}
            <div className="flex items-center gap-4">
                <button
                    onClick={handleSave}
                    className="px-8 py-3 bg-primary text-black rounded-full font-bold hover:bg-primary/90 transition-colors"
                >
                    Save Changes
                </button>
                {saved && (
                    <span className="text-primary font-medium">✓ Settings saved</span>
                )}
            </div>
        </div>
    );
}
