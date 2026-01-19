# Agentic Commerce UI Code Analysis Context

## Project Overview
AI-powered commerce platform for creating and minting NFT products on Arc blockchain.
Tech stack: Next.js 14, React, TailwindCSS, wagmi (Web3)

## Color Palette (globals.css + tailwind.config.js)

### Surface Colors (Dark Theme)
- surface-primary: #111827 (gray-900)
- surface-elevated: #1f2937 (gray-800)
- background: #0a0a0a (near black with mesh gradient)

### Arc Brand Colors
- arc-primary: #6366f1 (indigo-500)
- arc-secondary: #8b5cf6 (violet-500)
- arc-accent: #a855f7 (purple-500)

### Text Hierarchy
- text-primary: #f9fafb (white)
- text-secondary: #d1d5db (gray-300)
- text-muted: #9ca3af (gray-400)

### Borders
- border-subtle: #374151 (gray-700)
- border-default: #4b5563 (gray-600)

### Semantic Colors
- success: #22c55e
- warning: #f59e0b
- error: #ef4444
- info: #3b82f6

## Design System Patterns

### Glass Morphism
```css
.glass {
  background: rgba(17, 24, 39, 0.5);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(55, 65, 81, 0.5);
}
```

### Mesh Background
```css
.bg-arc-mesh {
  background-color: #0a0a0a;
  background-image:
    radial-gradient(at 27% 37%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
    radial-gradient(at 97% 21%, rgba(139, 92, 246, 0.1) 0px, transparent 50%),
    radial-gradient(at 52% 99%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
}
```

### Gradient Text
```css
.text-gradient {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

## Component Styles

### Button Variants
- primary: bg-arc-primary, white text, hover to secondary
- secondary: bg-gray-800, border-gray-700, hover to gray-700
- ghost: transparent, hover bg-gray-800
- destructive: bg-red-600, hover to red-700

### Card Pattern (ProductCard)
- bg-gray-800/50 with border-gray-700
- Hover: border-arc-primary/50, shadow-arc-primary/10
- Rounded-xl corners
- Image with scale-105 hover transition
- Quick View overlay on hover (black/50 bg)

### Chat Window
- Glass container with rounded-xl
- User messages: bg-arc-primary (purple bubble)
- Assistant messages: bg-gray-800 (dark bubble)
- Sparkles icon for AI branding
- Connection status indicator (green/yellow dot)

### Header
- Sticky glass header with h-16
- Logo with gradient background square + sparkles icon
- Navigation with gray-400 to white hover

### Sidebar
- Glass cards with rounded-xl, p-6
- Numbered steps with arc-primary/20 circles
- Stats in 2-column grid
- Featured grid with pulse placeholder animation

## Typography
- Font feature settings: 'rlig' 1, 'calt' 1
- Antialiased rendering
- Heading: font-bold/font-semibold
- Body: text-sm with gray-400 secondary

## Animations
- fade-in: 0.3s ease-in-out
- slide-up: 0.3s ease-out with translateY
- pulse-glow: 2s infinite with arc-primary box-shadow
- bounce: 1s infinite for loading dots

## Layout
- Container with mx-auto and px-4
- 3-column grid on lg: (2-col chat, 1-col sidebar)
- Min-h-screen flex-col for full height
- Responsive: hidden lg:block for sidebar

## Custom Scrollbar
- w-2 width
- bg-gray-900 track
- bg-gray-700 thumb with rounded-full
- Hover: bg-gray-600

## Key Components Code

### page.tsx - Main Layout
Three main sections:
1. Glass header with logo, nav, wallet button
2. Main area: 2-col chat + 1-col sidebar
3. Footer with links

### ChatWindow.tsx
- Suggestion prompt buttons (rounded-full, gray-800 bg)
- Message bubbles with avatar icons
- Streaming indicator with pulsing cursor
- Error display with red styling
- Input form at bottom

### ProductCard.tsx
- Aspect-square image container
- Loading spinner animation
- Hover overlay with Quick View button
- Price in arc-primary color
- NFT badge (top-right, arc-primary/20 bg)
