export default function Footer() {
    return (
        <footer className="py-12 bg-black border-t border-white/5">
            <div className="container px-4 mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="text-muted-foreground text-sm">
                    © 2026 SonicStream. All rights reserved.
                </div>
                <div className="flex gap-6 text-sm text-muted-foreground">
                    <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
                    <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
                    <a href="#" className="hover:text-primary transition-colors">Contact</a>
                </div>
            </div>
        </footer>
    );
}
