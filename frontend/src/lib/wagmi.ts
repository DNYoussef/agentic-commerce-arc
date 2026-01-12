import { QueryClient } from '@tanstack/react-query';
import { createAppKit } from '@reown/appkit';
import { WagmiAdapter } from '@reown/appkit-adapter-wagmi';
import type { AppKitNetwork } from '@reown/appkit-common';
import { createConfig, http } from 'wagmi';
import { injected, walletConnect } from 'wagmi/connectors';
import { defineChain } from 'viem';

const ARC_CHAIN_ID = Number(process.env.NEXT_PUBLIC_ARC_CHAIN_ID || 5042002);
const ARC_RPC_URL =
  process.env.NEXT_PUBLIC_ARC_RPC_URL ||
  process.env.NEXT_PUBLIC_ARC_RPC ||
  'https://rpc.testnet.arc.network';
const ARC_EXPLORER_URL =
  process.env.NEXT_PUBLIC_ARC_EXPLORER_URL || 'https://testnet.arcscan.app';

export const arcTestnet = defineChain({
  id: ARC_CHAIN_ID,
  name: 'Arc Testnet',
  network: 'arc-testnet',
  nativeCurrency: {
    name: 'ARC',
    symbol: 'ARC',
    decimals: 18,
  },
  rpcUrls: {
    default: { http: [ARC_RPC_URL] },
    public: { http: [ARC_RPC_URL] },
  },
  blockExplorers: {
    default: { name: 'Arc Explorer', url: ARC_EXPLORER_URL },
  },
  testnet: true,
});

const appKitNetwork: AppKitNetwork = {
  ...arcTestnet,
  chainNamespace: 'eip155',
  caipNetworkId: `eip155:${arcTestnet.id}`,
};

const WALLETCONNECT_PROJECT_ID =
  process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || '';

const wagmiConnectors = [
  injected(),
  ...(WALLETCONNECT_PROJECT_ID
    ? [
        walletConnect({
          projectId: WALLETCONNECT_PROJECT_ID,
          showQrModal: false,
        }),
      ]
    : []),
];

export const wagmiConfig = createConfig({
  chains: [arcTestnet],
  connectors: wagmiConnectors,
  transports: {
    [arcTestnet.id]: http(ARC_RPC_URL),
  },
});

export const queryClient = new QueryClient();

let appKitInstance: ReturnType<typeof createAppKit> | null = null;

export function initAppKit() {
  if (typeof window === 'undefined' || appKitInstance || !WALLETCONNECT_PROJECT_ID) {
    return;
  }

  const adapter = new WagmiAdapter({
    projectId: WALLETCONNECT_PROJECT_ID,
    networks: [appKitNetwork],
  });

  appKitInstance = createAppKit({
    adapters: [adapter],
    networks: [appKitNetwork],
    metadata: {
      name: 'Agentic Commerce on Arc',
      description: 'AI-powered shopping assistant on Arc',
      url: typeof window !== 'undefined' ? window.location.origin : '',
      icons: [],
    },
  });
}

export function getAppKit() {
  return appKitInstance;
}
