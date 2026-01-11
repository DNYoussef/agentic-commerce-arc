/**
 * Main Chat Page
 */

'use client';

import { WalletButton } from '@/components/WalletButton';
import { ChatWindow } from '@/components/ChatWindow';

// ============ COMPONENT ============

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 glass border-b border-gray-800/50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-arc-gradient flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gradient">
              Agentic Commerce
            </span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <a
              href="#"
              className="text-gray-400 hover:text-white transition-colors"
            >
              How It Works
            </a>
            <a
              href="#"
              className="text-gray-400 hover:text-white transition-colors"
            >
              Gallery
            </a>
            <a
              href="https://arc.tech"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors flex items-center gap-1"
            >
              Arc Chain
              <ExternalLinkIcon className="w-3 h-3" />
            </a>
          </nav>

          {/* Wallet */}
          <WalletButton />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Chat Area */}
          <div className="lg:col-span-2">
            <ChatWindow className="h-full" />
          </div>

          {/* Sidebar */}
          <aside className="hidden lg:block space-y-6">
            {/* Stats Card */}
            <div className="glass rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-white">Platform Stats</h3>
              <div className="grid grid-cols-2 gap-4">
                <StatCard label="Products Created" value="12,847" />
                <StatCard label="NFTs Minted" value="8,234" />
                <StatCard label="Total Volume" value="1.2M ARC" />
                <StatCard label="Active Users" value="3,456" />
              </div>
            </div>

            {/* How It Works */}
            <div className="glass rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-white">How It Works</h3>
              <ol className="space-y-3">
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-arc-primary/20 text-arc-primary text-sm flex items-center justify-center">
                    1
                  </span>
                  <span className="text-gray-400 text-sm">
                    Describe the product you want
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-arc-primary/20 text-arc-primary text-sm flex items-center justify-center">
                    2
                  </span>
                  <span className="text-gray-400 text-sm">
                    AI generates a unique product image
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-arc-primary/20 text-arc-primary text-sm flex items-center justify-center">
                    3
                  </span>
                  <span className="text-gray-400 text-sm">
                    Mint it as an NFT on Arc blockchain
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-arc-primary/20 text-arc-primary text-sm flex items-center justify-center">
                    4
                  </span>
                  <span className="text-gray-400 text-sm">
                    Trade or redeem for physical goods
                  </span>
                </li>
              </ol>
            </div>

            {/* Featured */}
            <div className="glass rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-white">Featured Creations</h3>
              <div className="grid grid-cols-3 gap-2">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div
                    key={i}
                    className="aspect-square rounded-lg bg-gray-800 animate-pulse"
                  />
                ))}
              </div>
              <button className="w-full text-sm text-arc-primary hover:text-arc-secondary transition-colors">
                View Gallery
              </button>
            </div>
          </aside>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 py-6">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-500 text-sm">
            2024 Agentic Commerce. Built on Arc blockchain.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="#"
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              Terms
            </a>
            <a
              href="#"
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              Privacy
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ============ SUB-COMPONENTS ============

interface StatCardProps {
  label: string;
  value: string;
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="text-center">
      <p className="text-lg font-bold text-white">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}

// ============ ICONS ============

function SparklesIcon({ className = '' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z" />
    </svg>
  );
}

function ExternalLinkIcon({ className = '' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  );
}
