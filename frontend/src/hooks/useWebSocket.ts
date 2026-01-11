/**
 * WebSocket Hook
 * Manages WebSocket connection for real-time chat streaming
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

// ============ TYPES ============

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketMessage {
  type: 'message' | 'stream_start' | 'stream_chunk' | 'stream_end' | 'error';
  data: unknown;
  timestamp: string;
}

export interface UseWebSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn {
  status: WebSocketStatus;
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  connect: () => void;
  disconnect: () => void;
  send: (data: unknown) => void;
  reconnectAttempts: number;
}

// ============ HOOK ============

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearReconnectTimeout();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (isMountedRef.current) {
      setStatus('disconnected');
    }
  }, [clearReconnectTimeout]);

  const connect = useCallback(() => {
    // Don't connect if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    clearReconnectTimeout();
    setStatus('connecting');

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (isMountedRef.current) {
          setStatus('connected');
          setReconnectAttempts(0);
          onConnect?.();
        }
      };

      ws.onclose = () => {
        if (isMountedRef.current) {
          setStatus('disconnected');
          onDisconnect?.();

          // Attempt reconnection
          if (reconnect && reconnectAttempts < maxReconnectAttempts) {
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isMountedRef.current) {
                setReconnectAttempts((prev) => prev + 1);
                connect();
              }
            }, reconnectInterval);
          }
        }
      };

      ws.onerror = (event) => {
        if (isMountedRef.current) {
          setStatus('error');
          onError?.(event);
        }
      };

      ws.onmessage = (event) => {
        if (isMountedRef.current) {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            setLastMessage(message);
            onMessage?.(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setStatus('error');
    }
  }, [
    url,
    reconnect,
    reconnectInterval,
    maxReconnectAttempts,
    reconnectAttempts,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    clearReconnectTimeout,
  ]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    isMountedRef.current = true;

    if (autoConnect) {
      connect();
    }

    return () => {
      isMountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    isConnected: status === 'connected',
    lastMessage,
    connect,
    disconnect,
    send,
    reconnectAttempts,
  };
}

export default useWebSocket;
