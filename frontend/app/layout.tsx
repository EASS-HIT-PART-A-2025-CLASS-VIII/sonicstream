import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { cn } from '@/lib/utils';
import { AuthProvider } from '@/lib/AuthContext';
import { PlayerProvider } from '@/lib/usePlayer';
import YouTubePlayerModal from '@/components/player/YouTubePlayerModal';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Music Discovery Platform',
  description: 'AI-Powered Music Recommendations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={cn(inter.className, "bg-background text-foreground min-h-screen antialiased")}>
        <AuthProvider>
          <PlayerProvider>
            {children}
            <YouTubePlayerModal />
          </PlayerProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
