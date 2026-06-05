/**
 * Root Layout
 */

import type { Metadata, Viewport } from 'next';
import { Providers } from './providers';
import './globals.css';

// ============ METADATA ============

export const metadata: Metadata = {
  title: 'Agentic Commerce | AI-Powered Shopping on Arc',
  description: 'Create AI-generated product concepts and test Arc escrow purchases. NFT minting is not shipped in this build.',
  keywords: ['AI', 'blockchain', 'Arc', 'commerce', 'shopping', 'generative AI', 'escrow'],
  authors: [{ name: 'Agentic Commerce Team' }],
  openGraph: {
    title: 'Agentic Commerce | AI-Powered Shopping on Arc',
    description: 'Create AI-generated product concepts and test Arc escrow purchases. NFT minting is not shipped in this build.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Agentic Commerce | AI-Powered Shopping on Arc',
    description: 'Create AI-generated product concepts and test Arc escrow purchases. NFT minting is not shipped in this build.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#6366f1',
};

// ============ LAYOUT ============

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-arc-mesh">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
