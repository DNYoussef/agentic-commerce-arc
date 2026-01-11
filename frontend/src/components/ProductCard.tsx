/**
 * ProductCard Component
 * Displays generated product images and information
 */

'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import type { ProductInfo } from '@/lib/api';

// ============ TYPES ============

interface ProductCardProps {
  product: ProductInfo;
  onPurchase?: (product: ProductInfo) => void;
  isPurchasing?: boolean;
  className?: string;
}

// ============ COMPONENT ============

export function ProductCard({
  product,
  onPurchase,
  isPurchasing = false,
  className,
}: ProductCardProps) {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handlePurchase = () => {
    onPurchase?.(product);
  };

  return (
    <>
      <div
        className={cn(
          'group relative overflow-hidden rounded-xl',
          'bg-gray-800/50 border border-gray-700',
          'hover:border-arc-primary/50 hover:shadow-lg hover:shadow-arc-primary/10',
          'transition-all duration-300',
          className
        )}
      >
        {/* Image Container */}
        <div className="relative aspect-square overflow-hidden">
          {!isImageLoaded && !imageError && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
              <div className="w-8 h-8 border-2 border-arc-primary border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {imageError ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
              <ImagePlaceholder className="w-16 h-16 text-gray-600" />
            </div>
          ) : (
            <img
              src={product.imageUrl || '/placeholder-product.png'}
              alt={product.name}
              className={cn(
                'w-full h-full object-cover',
                'group-hover:scale-105 transition-transform duration-300',
                isImageLoaded ? 'opacity-100' : 'opacity-0'
              )}
              onLoad={() => setIsImageLoaded(true)}
              onError={() => setImageError(true)}
            />
          )}

          {/* Quick View Overlay */}
          <div
            className={cn(
              'absolute inset-0 bg-black/50 flex items-center justify-center',
              'opacity-0 group-hover:opacity-100 transition-opacity duration-200'
            )}
          >
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsDialogOpen(true)}
            >
              Quick View
            </Button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-4 space-y-2">
          <h3 className="font-semibold text-white truncate">{product.name}</h3>
          <p className="text-sm text-gray-400 line-clamp-2">{product.description}</p>

          <div className="flex items-center justify-between pt-2">
            <span className="text-lg font-bold text-arc-primary">
              {product.price} ARC
            </span>

            <Button
              size="sm"
              onClick={handlePurchase}
              isLoading={isPurchasing}
              disabled={isPurchasing}
            >
              {isPurchasing ? 'Minting...' : 'Purchase'}
            </Button>
          </div>
        </div>

        {/* NFT Badge */}
        {product.contractAddress && (
          <div className="absolute top-3 right-3">
            <span className="px-2 py-1 text-xs font-medium bg-arc-primary/20 text-arc-primary rounded-full">
              NFT
            </span>
          </div>
        )}
      </div>

      {/* Detail Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent size="lg">
          <DialogHeader>
            <DialogTitle>{product.name}</DialogTitle>
            <DialogDescription>AI-Generated Product</DialogDescription>
          </DialogHeader>

          <DialogBody className="space-y-4">
            {/* Large Image */}
            <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-800">
              {product.imageUrl ? (
                <img
                  src={product.imageUrl}
                  alt={product.name}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <ImagePlaceholder className="w-24 h-24 text-gray-600" />
                </div>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-400">Description</h4>
              <p className="text-white">{product.description}</p>
            </div>

            {/* Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400">Price</h4>
                <p className="text-lg font-bold text-arc-primary">{product.price} ARC</p>
              </div>

              {product.contractAddress && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400">Contract</h4>
                  <p className="text-white font-mono text-sm truncate">
                    {product.contractAddress}
                  </p>
                </div>
              )}

              {product.tokenId && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400">Token ID</h4>
                  <p className="text-white font-mono">{product.tokenId}</p>
                </div>
              )}
            </div>
          </DialogBody>

          <DialogFooter>
            <DialogClose>Close</DialogClose>
            <Button onClick={handlePurchase} isLoading={isPurchasing}>
              {isPurchasing ? 'Minting...' : `Purchase for ${product.price} ARC`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// ============ ICONS ============

function ImagePlaceholder({ className = '' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </svg>
  );
}

export default ProductCard;
