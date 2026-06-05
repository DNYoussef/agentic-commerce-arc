import { act, renderHook, waitFor } from '@testing-library/react';
import { useWebSocket } from '@/hooks/useWebSocket';

type MockWebSocketInstance = {
  url: string;
  protocols?: string | string[];
  readyState: number;
  onopen: ((event: Event) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  send: jest.Mock;
  close: jest.Mock;
};

const websocketInstances: MockWebSocketInstance[] = [];

class MockWebSocket implements MockWebSocketInstance {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 3;

  url: string;
  protocols?: string | string[];
  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  send = jest.fn();
  close = jest.fn();

  constructor(url: string, protocols?: string | string[]) {
    this.url = url;
    this.protocols = protocols;
    websocketInstances.push(this);
  }
}

describe('useWebSocket auth transport smoke', () => {
  const originalWebSocket = global.WebSocket;

  beforeEach(() => {
    websocketInstances.length = 0;
    global.WebSocket = MockWebSocket as unknown as typeof WebSocket;
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    jest.clearAllMocks();
  });

  it('keeps bearer material out of the socket URL', async () => {
    const token = 'header.payload.signature';
    const url = 'wss://api.example.test/ws/chat/42?sessionId=session-1';

    renderHook(() =>
      useWebSocket({
        url,
        protocols: ['arc.jwt', token],
        reconnect: false,
      })
    );

    await waitFor(() => expect(websocketInstances.length).toBeGreaterThan(0));

    for (const websocket of websocketInstances) {
      expect(websocket.url).toBe(url);
      expect(websocket.url).not.toContain(token);
      expect(websocket.protocols).toEqual(['arc.jwt', token]);
    }
  });

  it('does not churn sockets when reconnect attempt state changes', async () => {
    jest.useFakeTimers();

    renderHook(() =>
      useWebSocket({
        url: 'wss://api.example.test/ws/chat/42',
        reconnect: true,
        reconnectInterval: 25,
        maxReconnectInterval: 25,
        maxReconnectAttempts: 2,
      })
    );

    await waitFor(() => expect(websocketInstances).toHaveLength(1));

    act(() => {
      websocketInstances[0].readyState = MockWebSocket.CLOSED;
      websocketInstances[0].onclose?.(new CloseEvent('close'));
    });

    act(() => {
      jest.advanceTimersByTime(25);
    });

    await waitFor(() => expect(websocketInstances).toHaveLength(2));

    act(() => {
      jest.runOnlyPendingTimers();
    });

    expect(websocketInstances).toHaveLength(2);
    jest.useRealTimers();
  });
});
