/**
 * ImageGenerator Component
 * UI for AI image generation.
 */

'use client';

import { useCallback, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';

interface ImageGeneratorProps {
  onUseImage?: (url: string) => void;
}

const STYLE_OPTIONS = ['product', 'lifestyle', 'minimalist', 'artistic'] as const;
const ASPECT_OPTIONS = ['1:1', '16:9', '4:3'] as const;

export function ImageGenerator({ onUseImage }: ImageGeneratorProps) {
  const { getValidAccessToken } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState<(typeof STYLE_OPTIONS)[number]>('product');
  const [aspectRatio, setAspectRatio] = useState<(typeof ASPECT_OPTIONS)[number]>('1:1');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const token = await getValidAccessToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/generate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            prompt: prompt.trim(),
            style,
            aspect_ratio: aspectRatio,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Image generation failed');
      }

      const data = (await response.json()) as { url?: string };
      setImageUrl(data.url ?? null);
    } catch (error) {
      setErrorMessage('Unable to generate image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [aspectRatio, getValidAccessToken, prompt, style]);

  return (
    <div className="space-y-4 rounded-xl border border-gray-800 bg-gray-900/60 p-6">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-white">Generate Product Image</h3>
        <p className="text-sm text-gray-400">
          Describe your product vision and choose a style to generate a new image.
        </p>
      </div>

      <Input
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Describe the image you want..."
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="space-y-1 text-sm text-gray-300">
          Style
          <select
            value={style}
            onChange={(event) =>
              setStyle(event.target.value as (typeof STYLE_OPTIONS)[number])
            }
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
          >
            {STYLE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1 text-sm text-gray-300">
          Aspect Ratio
          <select
            value={aspectRatio}
            onChange={(event) =>
              setAspectRatio(event.target.value as (typeof ASPECT_OPTIONS)[number])
            }
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
          >
            {ASPECT_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </div>

      <Button onClick={handleGenerate} isLoading={isLoading}>
        Generate Image
      </Button>

      {errorMessage && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300">
          {errorMessage}
        </div>
      )}

      {imageUrl && (
        <div className="space-y-3">
          <div className="overflow-hidden rounded-xl border border-gray-800">
            <img
              src={imageUrl}
              alt="Generated product"
              className="h-auto w-full cursor-zoom-in transition-transform hover:scale-105"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="secondary"
              onClick={() => window.open(imageUrl, '_blank')}
            >
              Download
            </Button>
            <Button
              variant="primary"
              onClick={() => onUseImage?.(imageUrl)}
            >
              Use as Product Image
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageGenerator;
