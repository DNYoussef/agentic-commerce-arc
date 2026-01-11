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
  walletAddress?: string;
  wsUrl?: string;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
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
    walletAddress,
    wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat',
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => initialSessionId || generateId());

  const streamingMessageRef = useRef<ChatMessage | null>(null);

  const handleWebSocketMessage = useCallback((wsMessage: WebSocketMessage) => {
    switch (wsMessage.type) {
      case 'stream_start': {
        setIsStreaming(true);
        setStreamingContent('');
        streamingMessageRef.current = {
          id: generateId(),
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
        };
        break;
      }

      case 'stream_chunk': {
        const chunk = wsMessage.data as { content: string };
        setStreamingContent((prev) => prev + chunk.content);
        if (streamingMessageRef.current) {
          streamingMessageRef.current.content += chunk.content;
        }
        break;
      }

      case 'stream_end': {
        setIsStreaming(false);
        setIsLoading(false);

        const endData = wsMessage.data as {
          products?: ProductInfo[];
          imageUrl?: string;
        };

        if (streamingMessageRef.current) {
          const finalMessage: ChatMessage = {
            ...streamingMessageRef.current,
            metadata: {
              products: endData.products,
              imageUrl: endData.imageUrl,
            },
          };

          setMessages((prev) => [...prev, finalMessage]);
          streamingMessageRef.current = null;
        }

        setStreamingContent('');
        break;
      }

      case 'message': {
        const messageData = wsMessage.data as ChatMessage;
        setMessages((prev) => [...prev, messageData]);
        setIsLoading(false);
        break;
      }

      case 'error': {
        const errorData = wsMessage.data as { message: string };
        setError(errorData.message);
        setIsLoading(false);
        setIsStreaming(false);
        break;
      }
    }
  }, []);

  const handleConnect = useCallback(() => {
    // Send session initialization
    send({
      type: 'init',
      sessionId,
      walletAddress,
    });
  }, [sessionId, walletAddress]);

  const handleError = useCallback(() => {
    setError('Connection lost. Trying to reconnect...');
  }, []);

  const { isConnected, send, status } = useWebSocket({
    url: `${wsUrl}?sessionId=${sessionId}`,
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
      });
    },
    [send, sessionId, walletAddress]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setStreamingContent('');
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
    error,
    sessionId,
    sendMessage,
    clearMessages,
    clearError,
    isConnected,
  };
}

export default useChat;
