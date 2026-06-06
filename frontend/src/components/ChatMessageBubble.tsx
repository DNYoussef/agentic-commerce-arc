import { ProductCard } from '@/components/ProductCard';
import { SparklesIcon, UserIcon } from '@/components/ChatIcons';
import { cn } from '@/lib/utils';
import type { ChatMessage, ProductInfo } from '@/lib/api';

interface ChatMessageBubbleProps {
  message: ChatMessage;
  onPurchase: (product: ProductInfo) => void;
  purchasingProductId: string | null;
}

export function ChatMessageBubble({
  message,
  onPurchase,
  purchasingProductId,
}: ChatMessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-gray-800 border border-gray-700' : 'bg-arc-primary'
        )}
      >
        {isUser ? (
          <UserIcon className="w-4 h-4 text-gray-400" />
        ) : (
          <SparklesIcon className="w-4 h-4 text-white" />
        )}
      </div>

      <div className={cn('flex-1 space-y-3', isUser && 'flex flex-col items-end')}>
        <div
          className={cn(
            'rounded-xl px-4 py-3 max-w-[80%] inline-block',
            isUser
              ? 'bg-gray-800 text-white border border-gray-700'
              : 'bg-arc-primary/10 text-white border border-arc-primary/20'
          )}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {message.metadata?.imageUrl && (
          <div className="rounded-xl overflow-hidden max-w-sm">
            <img
              src={message.metadata.imageUrl}
              alt="Generated product"
              className="w-full h-auto"
            />
          </div>
        )}

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
