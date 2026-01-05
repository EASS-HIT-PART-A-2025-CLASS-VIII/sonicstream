import { notFound } from "next/navigation";
import Image from "next/image";
import { getTrackById, getRecommendedTracks } from "@/lib/mockData";
import AudioFeaturesChart from "@/components/track/AudioFeaturesChart";
import SimilarTracks from "@/components/track/SimilarTracks";
import { Play, Heart, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TrackPage({ params }: { params: { id: string } }) {
    const track = getTrackById(params.id);

    if (!track) {
        notFound();
    }

    const similarTracks = getRecommendedTracks(track.id, 10);
    const minutes = Math.floor(track.duration / 60);
    const seconds = track.duration % 60;

    return (
        <div className="py-6">
            {/* Hero Section */}
            <div className="flex flex-col md:flex-row gap-8 mb-12">
                <div className="relative w-full md:w-80 aspect-square rounded-xl overflow-hidden shadow-2xl">
                    <Image
                        src={track.coverUrl}
                        alt={track.name}
                        fill
                        className="object-cover"
                        priority
                    />
                </div>

                <div className="flex flex-col justify-end">
                    <p className="text-sm font-semibold text-muted-foreground mb-2">SONG</p>
                    <h1 className="text-4xl md:text-6xl font-black mb-6 leading-tight">{track.name}</h1>
                    <div className="flex items-center gap-2 text-sm">
                        <span className="font-semibold">{track.artist}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{track.album}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{minutes}:{seconds.toString().padStart(2, '0')}</span>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4 mb-12">
                <Button size="lg" className="h-14 px-8 rounded-full bg-primary text-black hover:bg-primary/90 text-lg font-bold">
                    <Play className="mr-2 h-6 w-6 fill-black" />
                    Play
                </Button>
                <button className="h-14 w-14 rounded-full border border-white/10 hover:border-white/30 flex items-center justify-center transition-colors">
                    <Heart className="h-6 w-6" />
                </button>
                <button className="h-14 w-14 rounded-full border border-white/10 hover:border-white/30 flex items-center justify-center transition-colors">
                    <MoreHorizontal className="h-6 w-6" />
                </button>
            </div>

            {/* Audio Features */}
            <div className="mb-12">
                <AudioFeaturesChart features={track.audioFeatures} />
            </div>

            {/* Feature Details */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Danceability</p>
                    <p className="text-2xl font-bold">{Math.round(track.audioFeatures.danceability * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Energy</p>
                    <p className="text-2xl font-bold">{Math.round(track.audioFeatures.energy * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Valence</p>
                    <p className="text-2xl font-bold">{Math.round(track.audioFeatures.valence * 100)}%</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Tempo</p>
                    <p className="text-2xl font-bold">{Math.round(track.audioFeatures.tempo)} BPM</p>
                </div>
                <div className="bg-[#181818] p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Acousticness</p>
                    <p className="text-2xl font-bold">{Math.round(track.audioFeatures.acousticness * 100)}%</p>
                </div>
            </div>

            {/* Similar Tracks */}
            <SimilarTracks tracks={similarTracks} />
        </div>
    );
}
