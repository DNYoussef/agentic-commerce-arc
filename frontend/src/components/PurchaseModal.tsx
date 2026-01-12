/**
 * PurchaseModal Component
 * Handles one-click purchase flow with escrow creation.
 */

'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { parseUnits, formatUnits } from 'viem';
import {
  useAccount,
  usePublicClient,
  useReadContract,
  useWriteContract,
} from 'wagmi';
import type { ProductInfo } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

type TxStatus = 'idle' | 'approving' | 'pending' | 'confirmed' | 'failed';

interface PurchaseModalProps {
  product: ProductInfo;
  onClose: () => void;
  onSuccess: (txHash: string) => void;
}

const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';

export function PurchaseModal({ product, onClose, onSuccess }: PurchaseModalProps) {
  const { address } = useAccount();
  const publicClient = usePublicClient();
  const { writeContractAsync } = useWriteContract();

  const [status, setStatus] = useState<TxStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [gasEstimate, setGasEstimate] = useState<string | null>(null);

  const escrowAddress = process.env.NEXT_PUBLIC_ESCROW_CONTRACT as
    | `0x${string}`
    | undefined;
  const tokenAddress = process.env.NEXT_PUBLIC_TOKEN_ADDRESS as
    | `0x${string}`
    | undefined;
  const tokenSpenderAddress = process.env.NEXT_PUBLIC_TOKEN_SPENDER as
    | `0x${string}`
    | undefined;

  const priceAmount = useMemo(() => {
    const value = Number(product.price);
    return Number.isFinite(value) ? parseUnits(value.toString(), 6) : null;
  }, [product.price]);

  const { data: allowance, refetch: refetchAllowance } = useReadContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [
      (address ?? ZERO_ADDRESS) as `0x${string}`,
      (tokenSpenderAddress ?? ZERO_ADDRESS) as `0x${string}`,
    ],
    query: {
      enabled: Boolean(address && tokenAddress && tokenSpenderAddress),
    },
  });

  const isApproved = useMemo(() => {
    if (!priceAmount || allowance === undefined) return false;
    return BigInt(allowance as bigint) >= priceAmount;
  }, [allowance, priceAmount]);

  const estimateGas = useCallback(async () => {
    if (!publicClient || !escrowAddress || !priceAmount || !address) return;
    try {
      const gas = await publicClient.estimateContractGas({
        address: escrowAddress,
        abi: ESCROW_ABI,
        functionName: 'createEscrow',
        args: [product.sellerAddress ?? address, priceAmount],
        value: priceAmount,
      });
      setGasEstimate(formatUnits(gas, 0));
    } catch (error) {
      setGasEstimate(null);
      console.warn('Failed to estimate gas', error);
    }
  }, [address, escrowAddress, priceAmount, product.sellerAddress, publicClient]);

  useEffect(() => {
    void estimateGas();
  }, [estimateGas]);

  const handleApprove = useCallback(async () => {
    if (!tokenAddress || !tokenSpenderAddress || !priceAmount) return;
    setStatus('approving');
    setErrorMessage(null);
    try {
      const hash = await writeContractAsync({
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [tokenSpenderAddress, priceAmount],
      });
      await publicClient?.waitForTransactionReceipt({ hash });
      await refetchAllowance();
      setStatus('idle');
    } catch (error) {
      setStatus('failed');
      setErrorMessage('Approval failed. Please try again.');
    }
  }, [priceAmount, publicClient, refetchAllowance, tokenAddress, tokenSpenderAddress, writeContractAsync]);

  const handleConfirmPurchase = useCallback(async () => {
    if (!escrowAddress || !priceAmount || !address) return;
    setStatus('pending');
    setErrorMessage(null);
    try {
      const hash = await writeContractAsync({
        address: escrowAddress,
        abi: ESCROW_ABI,
        functionName: 'createEscrow',
        args: [product.sellerAddress ?? address, priceAmount],
        value: priceAmount,
      });
      await publicClient?.waitForTransactionReceipt({ hash });
      setStatus('confirmed');
      onSuccess(hash);
    } catch (error) {
      setStatus('failed');
      setErrorMessage('Purchase failed. Please try again.');
    }
  }, [address, escrowAddress, onSuccess, priceAmount, product.sellerAddress, publicClient, writeContractAsync]);

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent size="lg">
        <DialogHeader>
          <DialogTitle>Confirm Purchase</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 px-6 pb-2">
          <div className="flex gap-4">
            {product.imageUrl && (
              <img
                src={product.imageUrl}
                alt={product.name}
                className="h-24 w-24 rounded-lg object-cover"
              />
            )}
            <div className="space-y-1">
              <p className="text-lg font-semibold text-white">{product.name}</p>
              <p className="text-sm text-gray-400">{product.description}</p>
              <p className="text-sm text-gray-300">
                Price: {product.price} USDC
              </p>
              {gasEstimate && (
                <p className="text-xs text-gray-500">
                  Estimated gas: {gasEstimate}
                </p>
              )}
            </div>
          </div>

          {errorMessage && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300">
              {errorMessage}
            </div>
          )}

          <div className="rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3 text-sm text-gray-300">
            {isApproved
              ? 'USDC approval confirmed. Ready to purchase.'
              : 'Approve USDC to enable this purchase.'}
          </div>
        </div>

        <DialogFooter className="px-6 pb-6">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          {!isApproved && (
            <Button onClick={handleApprove} isLoading={status === 'approving'}>
              Approve USDC
            </Button>
          )}
          {isApproved && (
            <Button
              onClick={handleConfirmPurchase}
              isLoading={status === 'pending'}
            >
              Confirm Purchase
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

const ERC20_ABI = [
  {
    type: 'function',
    name: 'allowance',
    stateMutability: 'view',
    inputs: [
      { name: 'owner', type: 'address' },
      { name: 'spender', type: 'address' },
    ],
    outputs: [{ name: 'amount', type: 'uint256' }],
  },
  {
    type: 'function',
    name: 'approve',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ name: 'success', type: 'bool' }],
  },
];

const ESCROW_ABI = [
  {
    type: 'function',
    name: 'createEscrow',
    stateMutability: 'payable',
    inputs: [
      { name: 'seller', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ name: 'escrowId', type: 'uint256' }],
  },
];

export default PurchaseModal;
