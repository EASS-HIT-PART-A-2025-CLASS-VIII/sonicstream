import SearchBar from "@/components/dashboard/SearchBar";
import TrendingSection from "@/components/dashboard/TrendingSection";

export default function DashboardPage() {
    return (
        <div className="py-6">
            {/* Welcome Header */}
            <h1 className="text-3xl md:text-4xl font-bold mb-8">Good evening</h1>

            {/* Search */}
            <SearchBar />

            {/* Content */}
            <div className="space-y-12">
                <TrendingSection />

                {/* Placeholder for 'Made For You' or other sections */}
                <section>
                    <h2 className="text-2xl font-bold tracking-tight mb-6">Made For You</h2>
                    <div className="p-12 border border-dashed border-white/10 rounded-xl flex items-center justify-center text-muted-foreground">
                        Personalized AI recommendations will appear here.
                    </div>
                </section>
            </div>
        </div>
    );
}
