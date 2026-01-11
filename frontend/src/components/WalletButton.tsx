/**
 * WalletButton Component
 * Handles wallet connection with WalletConnect v2 via Reown AppKit
 */

'use client';

import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

// ============ TYPES ============

interface WalletButtonProps {
  className?: string;
}

// ============ COMPONENT ============

export function WalletButton({ className }: WalletButtonProps) {
  const {
    isConnected,
    isConnecting,
    formattedAddress,
    balance,
    isCorrectChain,
    connect,
    disconnect,
    switchToArc,
  } = useWallet();

  if (!isConnected) {
    return (
      <Button
        onClick={connect}
        isLoading={isConnecting}
        className={cn('min-w-[140px]', className)}
      >
        {isConnecting ? 'Connecting...' : 'Connect Wallet'}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            'flex items-center gap-3 px-4 py-2 rounded-lg',
            'bg-gray-800 border border-gray-700',
            'hover:bg-gray-700 hover:border-gray-600',
            'focus:outline-none focus:ring-2 focus:ring-arc-primary',
            'transition-colors',
            !isCorrectChain && 'border-yellow-500/50',
            className
          )}
        >
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'w-2 h-2 rounded-full',
                isCorrectChain ? 'bg-green-400' : 'bg-yellow-400'
              )}
            />
            <span className="text-white font-medium">{formattedAddress}</span>
          </div>
          <div className="text-gray-400 text-sm">
            {balance} ARC
          </div>
          <ChevronDownIcon className="w-4 h-4 text-gray-400" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Account</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {!isCorrectChain && (
          <>
            <DropdownMenuItem
              onClick={() => switchToArc()}
              icon={<AlertIcon className="w-4 h-4 text-yellow-400" />}
            >
              Switch to Arc Testnet
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}

        <DropdownMenuItem
          onClick={() => {
            if (formattedAddress) {
              navigator.clipboard.writeText(formattedAddress);
            }
          }}
          icon={<CopyIcon className="w-4 h-4" />}
        >
          Copy Address
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => window.open(`https://explorer-testnet.arc.tech/address/${formattedAddress}`, '_blank')}
          icon={<ExternalLinkIcon className="w-4 h-4" />}
        >
          View in Explorer
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => disconnect()}
          variant="destructive"
          icon={<DisconnectIcon className="w-4 h-4" />}
        >
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// ============ ICONS ============

function ChevronDownIcon({ className = '' }: { className?: string }) {
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
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function CopyIcon({ className = '' }: { className?: string }) {
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
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
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

function DisconnectIcon({ className = '' }: { className?: string }) {
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
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

function AlertIcon({ className = '' }: { className?: string }) {
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
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

export default WalletButton;
