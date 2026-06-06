export const SUGGESTION_PROMPTS = [
  'Create a futuristic sneaker',
  'Design a cyberpunk jacket',
  'Generate abstract digital art',
  'Create a minimalist watch',
];

export function formatToolLabel(toolName: string) {
  const normalized = toolName.replaceAll('_', ' ');
  if (normalized.includes('search')) return 'search products';
  if (normalized.includes('image') || normalized.includes('generate')) {
    return 'generate image';
  }
  if (normalized.includes('compare')) return 'compare prices';
  return normalized;
}

export function shortenHash(hash: string) {
  return hash.length > 14 ? `${hash.slice(0, 8)}...${hash.slice(-6)}` : hash;
}
