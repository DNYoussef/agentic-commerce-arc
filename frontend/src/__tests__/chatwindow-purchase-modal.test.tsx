import fs from 'node:fs';
import path from 'node:path';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { ChatWindow } from '@/components/ChatWindow';
import { useAuth } from '@/hooks/useAuth';
import { useChat } from '@/hooks/useChat';
import { useWallet } from '@/hooks/useWallet';

jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}));

jest.mock('@/hooks/useWallet', () => ({
  useWallet: jest.fn(),
}));

jest.mock('@/hooks/useChat', () => ({
  useChat: jest.fn(),
}));

jest.mock('@/components/ProductCard', () => ({
  ProductCard: ({ product, onPurchase, isPurchasing }: any) => (
    <button
      type="button"
      data-testid={`product-${product.id}`}
      data-purchasing={String(isPurchasing)}
      onClick={() => onPurchase(product)}
    >
      {product.name}
    </button>
  ),
}));

jest.mock('@/components/PurchaseModal', () => ({
  PurchaseModal: ({ product, onClose, onSuccess }: any) => (
    <div role="dialog" aria-label="purchase-modal">
      <span>{product.name}</span>
      <button type="button" onClick={() => onSuccess('0x1234567890abcdef')}>
        confirm purchase
      </button>
      <button type="button" onClick={onClose}>
        close
      </button>
    </div>
  ),
}));

const mockedUseAuth = useAuth as jest.Mock;
const mockedUseChat = useChat as jest.Mock;
const mockedUseWallet = useWallet as jest.Mock;

function arrangeChatWindow() {
  mockedUseAuth.mockReturnValue({
    tokens: { accessToken: 'test-token' },
  });
  mockedUseWallet.mockReturnValue({
    address: '0x0000000000000000000000000000000000000001',
    isConnected: true,
    isWalletConnected: true,
    isCorrectChain: true,
    connect: jest.fn(),
    switchToArc: jest.fn(),
  });
  mockedUseChat.mockReturnValue({
    messages: [
      {
        id: 'm1',
        role: 'assistant',
        content: 'Found a demo item.',
        timestamp: '2026-06-05T00:00:00.000Z',
        metadata: {
          products: [
            {
              id: 'p1',
              name: 'Arc Test Item',
              description: 'Demo product',
              price: '0.1',
            },
          ],
        },
      },
    ],
    isLoading: false,
    isStreaming: false,
    streamingContent: '',
    activeTool: null,
    error: null,
    sendMessage: jest.fn(),
    clearMessages: jest.fn(),
    clearError: jest.fn(),
    isConnected: true,
  });
}

describe('ChatWindow purchase flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
    arrangeChatWindow();
  });

  it('opens the shipped PurchaseModal when a product is purchased', () => {
    render(<ChatWindow />);

    fireEvent.click(screen.getByTestId('product-p1'));

    const dialog = screen.getByRole('dialog', { name: 'purchase-modal' });
    expect(dialog).toBeInTheDocument();
    expect(within(dialog).getByText('Arc Test Item')).toBeInTheDocument();
    expect(screen.getByTestId('product-p1')).toHaveAttribute('data-purchasing', 'true');

    fireEvent.click(screen.getByRole('button', { name: 'confirm purchase' }));

    expect(screen.queryByRole('dialog', { name: 'purchase-modal' })).not.toBeInTheDocument();
    expect(screen.getByText(/Purchase submitted: 0x123456...abcdef/)).toBeInTheDocument();
  });

  it('keeps escrow contract writes out of ChatWindow', () => {
    const source = fs.readFileSync(
      path.join(process.cwd(), 'src/components/ChatWindow.tsx'),
      'utf8'
    );

    expect(source).toContain("import { PurchaseModal }");
    expect(source).not.toContain('useWriteContract');
    expect(source).not.toContain('parseEther');
    expect(source).not.toContain('SIMPLE_ESCROW_ABI');
    expect(source).not.toContain('ERC20_ABI');
    expect(source).not.toContain("functionName: 'createEscrow'");
  });
});
