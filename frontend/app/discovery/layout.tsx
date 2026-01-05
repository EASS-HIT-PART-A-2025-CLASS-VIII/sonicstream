import Sidebar from "@/components/layout/Sidebar";
import MobileNav from "@/components/layout/MobileNav";

export default function DiscoveryLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-black text-white">
            <Sidebar />
            <main className="md:pl-64 pb-20 md:pb-0 min-h-screen">
                <div className="container mx-auto p-6 md:p-10 max-w-7xl">
                    {children}
                </div>
            </main>
            <MobileNav />
        </div>
    );
}
