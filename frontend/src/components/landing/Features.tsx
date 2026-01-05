import { Zap, Music, BarChart3 } from "lucide-react";

const features = [
    {
        icon: Zap,
        title: "Instant Analysis",
        description: "Our engine processes audio features in milliseconds to find the perfect match."
    },
    {
        icon: Music,
        title: "8 Million Tracks",
        description: "Access a massive library of songs, from global hits to underground gems."
    },
    {
        icon: BarChart3,
        title: "Deep Analytics",
        description: "Visualize song DNA with professional radar charts and audio metrics."
    }
];

export default function Features() {
    return (
        <section className="py-24 bg-black">
            <div className="container px-4 mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {features.map((f, i) => (
                        <div key={i} className="group p-8 rounded-3xl bg-white/5 border border-white/5 hover:border-primary/50 transition-colors duration-300">
                            <div className="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary text-primary group-hover:text-black transition-colors">
                                <f.icon className="h-6 w-6" />
                            </div>
                            <h3 className="text-xl font-bold mb-3">{f.title}</h3>
                            <p className="text-muted-foreground leading-relaxed">{f.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
