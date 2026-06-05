import { act, renderHook, waitFor } from '@testing-library/react';
import { useChat } from '@/hooks/useChat';

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

function createJwtWithSubject(subject: string): string {
  const payload = btoa(JSON.stringify({ sub: subject }));
  return `header.${payload}.signature`;
}

describe('useChat WebSocket authentication', () => {
  const originalWebSocket = global.WebSocket;

  beforeEach(() => {
    websocketInstances.length = 0;
    global.WebSocket = MockWebSocket as unknown as typeof WebSocket;
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    jest.clearAllMocks();
  });

  it('sends JWTs via WebSocket subprotocols instead of URL or message payloads', async () => {
    const token = createJwtWithSubject('42');
    const { result } = renderHook(() =>
      useChat({
        sessionId: 'session-1',
        userId: 'wallet-user',
        walletAddress: '0xabc',
        wsUrl: 'ws://api.test/ws/chat',
        accessToken: token,
      })
    );

    await waitFor(() => expect(websocketInstances).toHaveLength(1));
    const websocket = websocketInstances[0];

    expect(websocket.url).toBe('ws://api.test/ws/chat/42?sessionId=session-1');
    expect(websocket.url).not.toContain(token);
    expect(websocket.protocols).toEqual(['arc.jwt', token]);

    websocket.readyState = MockWebSocket.OPEN;
    act(() => {
      websocket.onopen?.(new Event('open'));
    });

    expect(JSON.parse(websocket.send.mock.calls[0][0])).toEqual({
      type: 'init',
      sessionId: 'session-1',
      walletAddress: '0xabc',
    });

    websocket.send.mockClear();
    act(() => {
      result.current.sendMessage('find a keyboard');
    });

    expect(JSON.parse(websocket.send.mock.calls[0][0])).toEqual({
      type: 'message',
      sessionId: 'session-1',
      walletAddress: '0xabc',
      content: 'find a keyboard',
    });
  });
});
