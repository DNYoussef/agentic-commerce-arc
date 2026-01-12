/**
 * Chat Hook
 * Manages chat state and message handling
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { generateId } from '@/lib/utils';
import { useWebSocket, type WebSocketMessage } from './useWebSocket';
import type { ChatMessage, ProductInfo } from '@/lib/api';

// ============ TYPES ============

export interface UseChatOptions {
  sessionId?: string;
  userId?: string;
  walletAddress?: string;
  wsUrl?: string;
  accessToken?: string | null;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
  activeTool: string | null;
  error: string | null;
  sessionId: string;
  sendMessage: (content: string) => void;
  clearMessages: () => void;
  clearError: () => void;
  isConnected: boolean;
}

// ============ HOOK ============

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const {
    sessionId: initialSessionId,
    userId: initialUserId,
    walletAddress,
    wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat',
    accessToken,
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => initialSessionId || generateId());
  const [userId] = useState(() => initialUserId || walletAddress || sessionId);

  const streamingMessageRef = useRef<ChatMessage | null>(null);
  const pendingProductsRef = useRef<ProductInfo[]>([]);
  const pendingImageRef = useRef<string | null>(null);

  const handleWebSocketMessage = useCallback((wsMessage: WebSocketMessage) => {
    const payload = wsMessage.data ?? wsMessage.content;
    const content = typeof payload === 'string' ? payload : '';
    const messageData = payload as { content?: string; message?: string; tool?: string; data?: unknown } | undefined;
    const errorMessage = messageData?.message || messageData?.content || content;

    switch (wsMessage.type) {
      case 'text': {
        if (!streamingMessageRef.current) {
          streamingMessageRef.current = {
            id: generateId(),
            role: 'assistant',
            content: '',
            timestamp: new Date().toISOString(),
          };
        }
        setIsStreaming(true);
        setStreamingContent((prev) => prev + content);
        streamingMessageRef.current.content += content;
        break;
      }
      case 'tool_start': {
        const toolName = wsMessage.tool ?? messageData?.tool ?? (payload as { tool?: string } | undefined)?.tool;
        if (toolName) {
          setActiveTool(toolName);
        }
        break;
      }
      case 'tool_result': {
        setActiveTool(null);
        break;
      }
      case 'products': {
        const products = Array.isArray(wsMessage.data)
          ? (wsMessage.data as ProductInfo[])
          : (payload as { data?: ProductInfo[] } | undefined)?.data;
        if (products?.length) {
          pendingProductsRef.current = normalizeProducts(products);
        }
        break;
      }
      case 'image': {
        const imageData =
          (wsMessage.data as { url?: string; image_url?: string } | undefined) ??
          (payload as { data?: { url?: string; image_url?: string } } | undefined)?.data;
        const url = imageData?.url ?? imageData?.image_url;
        if (url) {
          pendingImageRef.current = url;
        }
        break;
      }
      case 'done': {
        setIsStreaming(false);
        setIsLoading(false);
        setActiveTool(null);

        if (streamingMessageRef.current) {
          const finalMessage: ChatMessage = {
            ...streamingMessageRef.current,
            metadata: {
              products: pendingProductsRef.current.length
                ? pendingProductsRef.current
                : undefined,
              imageUrl: pendingImageRef.current ?? undefined,
            },
          };
          setMessages((prev) => [...prev, finalMessage]);
        }

        streamingMessageRef.current = null;
        pendingProductsRef.current = [];
        pendingImageRef.current = null;
        setStreamingContent('');
        break;
      }
      case 'message': {
        const messagePayload = payload as ChatMessage;
        if (messagePayload?.content) {
          setMessages((prev) => [...prev, messagePayload]);
        }
        setIsLoading(false);
        break;
      }
      case 'error': {
        setError(errorMessage || 'An unexpected error occurred.');
        setIsLoading(false);
        setIsStreaming(false);
        setActiveTool(null);
        break;
      }
      case 'pong':
      default:
        break;
    }
  }, []);

  const handleConnect = useCallback(() => {
    const initPayload = {
      type: 'init',
      sessionId,
      walletAddress,
      token: accessToken ?? undefined,
    };
    send({
      ...initPayload,
    });
  }, [accessToken, sessionId, walletAddress]);

  const handleError = useCallback(() => {
    setError('Connection lost. Trying to reconnect...');
  }, []);

  const { isConnected, send } = useWebSocket({
    url: `${wsUrl.replace(/\/$/, '')}/${userId}?sessionId=${sessionId}`,
    autoConnect: true,
    reconnect: true,
    onMessage: handleWebSocketMessage,
    onConnect: handleConnect,
    onError: handleError,
  });

  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) return;

      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      send({
        type: 'message',
        sessionId,
        walletAddress,
        content: content.trim(),
        token: accessToken ?? undefined,
      });
    },
    [accessToken, send, sessionId, walletAddress]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setIsLoading(false);
    setIsStreaming(false);
    setStreamingContent('');
    streamingMessageRef.current = null;
    pendingProductsRef.current = [];
    pendingImageRef.current = null;
    setActiveTool(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Clear error when reconnected
  useEffect(() => {
    if (isConnected && error?.includes('reconnect')) {
      setError(null);
    }
  }, [isConnected, error]);

  return {
    messages,
    isLoading,
    isStreaming,
    streamingContent,
    activeTool,
    error,
    sessionId,
    sendMessage,
    clearMessages,
    clearError,
    isConnected,
  };
}

function normalizeProducts(products: ProductInfo[]): ProductInfo[] {
  return products.map((product) => ({
    ...product,
    imageUrl:
      product.imageUrl ||
      (product as { image_url?: string }).image_url,
  }));
}

export default useChat;
