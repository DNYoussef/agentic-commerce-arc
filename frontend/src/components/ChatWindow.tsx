/**
 * ChatWindow Component
 * Streaming chat interface with WebSocket connection
 */

'use client';

import { useRef, useEffect, useState, useCallback, FormEvent } from 'react';
import { parseEther, maxUint256 } from 'viem';
import { useWriteContract } from 'wagmi';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/hooks/useAuth';
import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ProductCard } from '@/components/ProductCard';
import type { ChatMessage, ProductInfo } from '@/lib/api';

// ============ TYPES ============

interface ChatWindowProps {
  className?: string;
}

// ============ COMPONENT ============

export function ChatWindow({ className }: ChatWindowProps) {
  const [inputValue, setInputValue] = useState('');
  const [purchasingProductId, setPurchasingProductId] = useState<string | null>(
    null
  );
  const [hasApproved, setHasApproved] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    address,
    isConnected: isWalletConnected,
    isCorrectChain,
    connect,
    switchToArc,
  } = useWallet();
  const { tokens } = useAuth();
  const {
    messages,
    isLoading,
    isStreaming,
    streamingContent,
    activeTool,
    error,
    sendMessage,
    clearMessages,
    clearError,
    isConnected: isChatConnected,
  } = useChat({
    walletAddress: address,
    userId: address ?? 'guest',
    accessToken: tokens?.accessToken ?? null,
  });
  const { writeContractAsync } = useWriteContract();

  const escrowContractAddress = process.env.NEXT_PUBLIC_ESCROW_CONTRACT as
    | `0x${string}`
    | undefined;
  const defaultSellerAddress = process.env.NEXT_PUBLIC_ESCROW_SELLER as
    | `0x${string}`
    | undefined;
  const tokenAddress = process.env.NEXT_PUBLIC_TOKEN_ADDRESS as
    | `0x${string}`
    | undefined;
  const tokenSpenderAddress = process.env.NEXT_PUBLIC_TOKEN_SPENDER as
    | `0x${string}`
    | undefined;

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    setHasApproved(window.localStorage.getItem('arc-token-approved') === 'true');
  }, []);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (inputValue.trim() && !isLoading) {
        sendMessage(inputValue);
        setInputValue('');
      }
    },
    [inputValue, isLoading, sendMessage]
  );

  const handlePurchase = useCallback(
    async (product: ProductInfo) => {
      if (!isWalletConnected) {
        connect();
        return;
      }

      if (!isCorrectChain) {
        await switchToArc();
        return;
      }

      if (tokenAddress && tokenSpenderAddress && !hasApproved) {
        try {
          await writeContractAsync({
            abi: ERC20_ABI,
            address: tokenAddress,
            functionName: 'approve',
            args: [tokenSpenderAddress, maxUint256],
          });
          setHasApproved(true);
          if (typeof window !== 'undefined') {
            window.localStorage.setItem('arc-token-approved', 'true');
          }
        } catch (error) {
          console.error('Approval failed:', error);
          return;
        }
      }

      if (!escrowContractAddress) {
        console.warn('Missing escrow contract address.');
        return;
      }

      const sellerAddress =
        (product as { sellerAddress?: `0x${string}` }).sellerAddress ??
        defaultSellerAddress;

      if (!sellerAddress) {
        console.warn('Missing seller address for purchase.');
        return;
      }

      if (purchasingProductId) {
        return;
      }

      const priceValue = Number(product.price);
      if (!Number.isFinite(priceValue)) {
        console.warn('Invalid product price:', product.price);
        return;
      }

      try {
        setPurchasingProductId(product.id);
        const amount = parseEther(priceValue.toString());

        await writeContractAsync({
          abi: SIMPLE_ESCROW_ABI,
          address: escrowContractAddress,
          functionName: 'createEscrow',
          args: [sellerAddress, amount],
          value: amount,
        });
      } catch (error) {
        console.error('Purchase failed:', error);
      } finally {
        setPurchasingProductId(null);
      }
    },
    [
      connect,
      defaultSellerAddress,
      escrowContractAddress,
      hasApproved,
      isWalletConnected,
      isCorrectChain,
      purchasingProductId,
      switchToArc,
      tokenAddress,
      tokenSpenderAddress,
      writeContractAsync,
    ]
  );

  const handleClearChat = useCallback(() => {
    clearMessages();
    setInputValue('');
    inputRef.current?.focus();
  }, [clearMessages]);

  return (
    <div
      className={cn(
        'flex flex-col h-full',
        'bg-gray-900/50 rounded-xl border border-gray-800',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'w-2 h-2 rounded-full',
              isChatConnected ? 'bg-green-400' : 'bg-yellow-400'
            )}
          />
          <span className="text-sm text-gray-400">
            {isChatConnected ? 'Connected' : 'Connecting...'}
          </span>
        </div>

        <h2 className="font-semibold text-white">AI Shopping Assistant</h2>

        <button
          onClick={handleClearChat}
          disabled={messages.length === 0 && !isStreaming && !isLoading}
          className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Welcome Message */}
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-arc-primary/20 flex items-center justify-center">
              <SparklesIcon className="w-8 h-8 text-arc-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-white">
                Welcome to Agentic Commerce
              </h3>
              <p className="text-gray-400 max-w-md">
                Describe the product you want and I&apos;ll generate a unique AI-created
                item for you. You can then mint it as an NFT on the Arc blockchain.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTION_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  className={cn(
                    'px-3 py-1.5 text-sm rounded-full',
                    'bg-gray-800 text-gray-300 border border-gray-700',
                    'hover:bg-gray-700 hover:text-white hover:border-gray-600',
                    'transition-colors'
                  )}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message List */}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onPurchase={handlePurchase}
            purchasingProductId={purchasingProductId}
          />
        ))}

        {/* Streaming Message */}
        {isStreaming && (streamingContent || activeTool) && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-arc-primary/20 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-4 h-4 text-arc-primary" />
            </div>
            <div className="flex-1 space-y-2">
              <div className="bg-gray-800 rounded-xl px-4 py-3 text-white">
                {streamingContent || 'Thinking...'}
                <span className="inline-block w-2 h-4 ml-1 bg-arc-primary animate-pulse" />
              </div>
              {activeTool && (
                <div className="text-xs text-gray-400">
                  Using tool: {formatToolLabel(activeTool)}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && !isStreaming && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-arc-primary/20 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-4 h-4 text-arc-primary" />
            </div>
            <div className="flex-1">
              <div className="bg-gray-800 rounded-xl px-4 py-3 inline-flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-arc-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-arc-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-arc-primary rounded-full animate-bounce" />
                </div>
                <span className="text-gray-400 text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-center justify-center p-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-lg">
              <AlertIcon className="w-4 h-4 text-red-400" />
              <span className="text-red-400 text-sm">{error}</span>
              <button
                onClick={clearError}
                className="ml-2 text-red-400 hover:text-red-300"
              >
                <CloseIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
        <div className="flex gap-3">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe the product you want..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            isLoading={isLoading}
          >
            Send
          </Button>
        </div>
      </form>
    </div>
  );
}

// ============ SUB-COMPONENTS ============

interface MessageBubbleProps {
  message: ChatMessage;
  onPurchase: (product: ProductInfo) => void;
  purchasingProductId: string | null;
}

function MessageBubble({
  message,
  onPurchase,
  purchasingProductId,
}: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-gray-700' : 'bg-arc-primary/20'
        )}
      >
        {isUser ? (
          <UserIcon className="w-4 h-4 text-gray-300" />
        ) : (
          <SparklesIcon className="w-4 h-4 text-arc-primary" />
        )}
      </div>

      {/* Content */}
      <div className={cn('flex-1 space-y-3', isUser && 'flex flex-col items-end')}>
        <div
          className={cn(
            'rounded-xl px-4 py-3 max-w-[80%] inline-block',
            isUser
              ? 'bg-arc-primary text-white'
              : 'bg-gray-800 text-white'
          )}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Generated Image */}
        {message.metadata?.imageUrl && (
          <div className="rounded-xl overflow-hidden max-w-sm">
            <img
              src={message.metadata.imageUrl}
              alt="Generated product"
              className="w-full h-auto"
            />
          </div>
        )}

        {/* Products Grid */}
        {message.metadata?.products && message.metadata.products.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
            {message.metadata.products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onPurchase={onPurchase}
                isPurchasing={purchasingProductId === product.id}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============ CONSTANTS ============

const SUGGESTION_PROMPTS = [
  'Create a futuristic sneaker',
  'Design a cyberpunk jacket',
  'Generate abstract digital art',
  'Create a minimalist watch',
];

function formatToolLabel(toolName: string) {
  const normalized = toolName.replaceAll('_', ' ');
  if (normalized.includes('search')) return 'search products';
  if (normalized.includes('image') || normalized.includes('generate')) {
    return 'generate image';
  }
  if (normalized.includes('compare')) return 'compare prices';
  return normalized;
}

const SIMPLE_ESCROW_ABI = [
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

const ERC20_ABI = [
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

function UserIcon({ className = '' }: { className?: string }) {
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
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
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
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function CloseIcon({ className = '' }: { className?: string }) {
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
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default ChatWindow;
