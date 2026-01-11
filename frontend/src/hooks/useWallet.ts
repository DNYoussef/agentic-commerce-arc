/**
 * Wallet Hook
 * Provides wallet connection state and actions using Reown AppKit
 */

'use client';

import { useCallback, useEffect, useState } from 'react';
import { useAccount, useDisconnect, useBalance } from 'wagmi';
import { getAppKit, arcTestnet } from '@/lib/wagmi';
import { formatAddress, formatTokenAmount } from '@/lib/utils';

// ============ TYPES ============

export interface WalletState {
  isConnected: boolean;
  isConnecting: boolean;
  address: string | undefined;
  formattedAddress: string;
  balance: string;
  balanceRaw: bigint;
  chainId: number | undefined;
  isCorrectChain: boolean;
}

export interface UseWalletReturn extends WalletState {
  connect: () => void;
  disconnect: () => Promise<void>;
  switchToArc: () => Promise<void>;
}

// ============ HOOK ============

export function useWallet(): UseWalletReturn {
  const [isConnecting, setIsConnecting] = useState(false);

  const { address, isConnected, chainId } = useAccount();
  const { disconnectAsync } = useDisconnect();
  const { data: balanceData } = useBalance({
    address,
    chainId: arcTestnet.id,
  });

  const isCorrectChain = chainId === arcTestnet.id;

  const formattedAddress = address ? formatAddress(address) : '';
  const balance = balanceData
    ? formatTokenAmount(balanceData.value, balanceData.decimals)
    : '0';
  const balanceRaw = balanceData?.value ?? BigInt(0);

  const connect = useCallback(() => {
    const appKit = getAppKit();
    if (appKit) {
      setIsConnecting(true);
      appKit.open();
    }
  }, []);

  const disconnect = useCallback(async () => {
    try {
      await disconnectAsync();
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  }, [disconnectAsync]);

  const switchToArc = useCallback(async () => {
    const appKit = getAppKit();
    if (appKit) {
      try {
        await appKit.switchNetwork(arcTestnet);
      } catch (error) {
        console.error('Failed to switch network:', error);
      }
    }
  }, []);

  // Reset connecting state when connection status changes
  useEffect(() => {
    if (isConnected) {
      setIsConnecting(false);
    }
  }, [isConnected]);

  return {
    isConnected,
    isConnecting,
    address,
    formattedAddress,
    balance,
    balanceRaw,
    chainId,
    isCorrectChain,
    connect,
    disconnect,
    switchToArc,
  };
}

export default useWallet;
