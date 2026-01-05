"use client"

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { AudioFeatures } from '@/lib/mockData';

interface AudioFeaturesChartProps {
    features: AudioFeatures;
}

export default function AudioFeaturesChart({ features }: AudioFeaturesChartProps) {
    const data = [
        { feature: 'Danceability', value: features.danceability * 100, fullMark: 100 },
        { feature: 'Energy', value: features.energy * 100, fullMark: 100 },
        { feature: 'Valence', value: features.valence * 100, fullMark: 100 },
        { feature: 'Acousticness', value: features.acousticness * 100, fullMark: 100 },
        { feature: 'Tempo', value: (features.tempo / 200) * 100, fullMark: 100 }, // Normalize tempo
    ];

    return (
        <div className="w-full h-[400px] bg-[#181818] rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4">Audio Features</h3>
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={data}>
                    <PolarGrid stroke="#282828" />
                    <PolarAngleAxis
                        dataKey="feature"
                        tick={{ fill: '#a7a7a7', fontSize: 12 }}
                    />
                    <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fill: '#a7a7a7' }}
                    />
                    <Radar
                        name="Features"
                        dataKey="value"
                        stroke="#1ed760"
                        fill="#1ed760"
                        fillOpacity={0.3}
                        strokeWidth={2}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}
