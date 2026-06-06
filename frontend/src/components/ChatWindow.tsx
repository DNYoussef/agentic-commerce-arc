/**
 * ChatWindow Component
 * Streaming chat interface with WebSocket connection
 */

'use client';

import { useRef, useEffect, useState, useCallback, FormEvent } from 'react';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/hooks/useAuth';
import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PurchaseModal } from '@/components/PurchaseModal';
import { ChatMessageBubble } from '@/components/ChatMessageBubble';
import { AlertIcon, CloseIcon, SparklesIcon } from '@/components/ChatIcons';
import {
  SUGGESTION_PROMPTS,
  formatToolLabel,
  shortenHash,
} from '@/components/chatWindowFormat';
import type { ProductInfo } from '@/lib/api';

// ============ TYPES ============

interface ChatWindowProps {
  className?: string;
}

// ============ COMPONENT ============

export function ChatWindow({ className }: ChatWindowProps) {
  const [inputValue, setInputValue] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<ProductInfo | null>(null);
  const [lastPurchaseTxHash, setLastPurchaseTxHash] = useState<string | null>(null);
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
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
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
    (product: ProductInfo) => {
      if (!isWalletConnected) {
        connect();
        return;
      }

      if (!isCorrectChain) {
        void switchToArc();
        return;
      }

      setLastPurchaseTxHash(null);
      setSelectedProduct(product);
    },
    [
      connect,
      isWalletConnected,
      isCorrectChain,
      switchToArc,
    ]
  );

  const handlePurchaseSuccess = useCallback((txHash: string) => {
    setLastPurchaseTxHash(txHash);
    setSelectedProduct(null);
  }, []);

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
                item for you. You can inspect demo catalog items and purchase through
                Arc escrow where configured; NFT minting is not shipped in this build.
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
          <ChatMessageBubble
            key={message.id}
            message={message}
            onPurchase={handlePurchase}
            purchasingProductId={selectedProduct?.id ?? null}
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

        {lastPurchaseTxHash && (
          <div className="flex items-center justify-center p-2">
            <div className="px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg text-green-300 text-sm">
              Purchase submitted: {shortenHash(lastPurchaseTxHash)}
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

      {selectedProduct && (
        <PurchaseModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onSuccess={handlePurchaseSuccess}
        />
      )}
    </div>
  );
}

export default ChatWindow;
