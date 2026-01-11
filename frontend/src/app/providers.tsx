/**
 * App Providers
 * Wraps the app with necessary context providers
 */

'use client';

import { ReactNode, useEffect, useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { queryClient, wagmiConfig, initAppKit } from '@/lib/wagmi';

// ============ TYPES ============

interface ProvidersProps {
  children: ReactNode;
}

// ============ COMPONENT ============

export function Providers({ children }: ProvidersProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Initialize AppKit on client side
    initAppKit();
    setMounted(true);
  }, []);

  // Prevent hydration mismatch by only rendering on client
  if (!mounted) {
    return null;
  }

  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default Providers;
