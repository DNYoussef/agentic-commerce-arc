export interface ProductInfo {
  id: string;
  name: string;
  description?: string;
  price: number | string;
  imageUrl?: string;
  contractAddress?: string;
  tokenId?: string | number;
  sellerAddress?: `0x${string}`;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    products?: ProductInfo[];
    imageUrl?: string;
  };
}
