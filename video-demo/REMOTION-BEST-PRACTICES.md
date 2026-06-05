# Remotion Best Practices Guide

## Research-Based Enhancements Applied

This document summarizes the best practices researched and applied to the ARC video project.

---

## 1. Performance Optimization

### Avoid GPU-Heavy CSS Effects
Cloud rendering instances lack GPUs. These effects cause significant slowdowns:

| Avoid | Alternative |
|-------|-------------|
| `filter: blur()` | Solid semi-transparent backgrounds |
| `box-shadow` | Solid borders with opacity |
| `text-shadow` | Text with solid background |
| `filter: drop-shadow()` | Border effects |
| Complex gradients | Simple linear/radial gradients |

**Applied**: All components use solid colors and simple gradients only.

### Video Component Selection
```tsx
// OLD (slower)
import { Video } from "remotion";
<Video src={staticFile("demo.mp4")} />

// NEW (faster - use this!)
import { OffthreadVideo } from "remotion";
<OffthreadVideo src={staticFile("demo.mp4")} />
```

**Applied**: DemoVideo.tsx uses `OffthreadVideo` for the screen recording.

### Concurrency Optimization
```bash
# Find optimal concurrency for your machine
npx remotion benchmark

# Use discovered value
npx remotion render --concurrency=4 ...
```

### Resolution Scaling
For faster test renders, use `--scale`:
```bash
# Half resolution for quick preview
npx remotion render --scale=0.5 ...
```

---

## 2. Animation Best Practices

### Spring Animations for Natural Motion
```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const value = spring({
  frame,
  fps,
  config: {
    damping: 12,    // Higher = less bounce
    stiffness: 100, // Higher = faster
    mass: 0.8,      // Higher = slower, more inertia
  },
});
```

**Config Guidelines**:
| Effect | damping | stiffness | mass |
|--------|---------|-----------|------|
| Quick snap | 15-20 | 150+ | 0.3-0.5 |
| Smooth enter | 10-15 | 80-100 | 0.5-1.0 |
| Bouncy | 5-10 | 100+ | 0.5-1.0 |
| Slow reveal | 20+ | 50-80 | 1.0+ |

**Applied**: All animations use spring with appropriate configs.

### Easing for Enter/Exit
```tsx
import { interpolate, Easing } from "remotion";

// Enter: easeOut feels responsive
const enterOpacity = interpolate(frame, [0, 30], [0, 1], {
  easing: Easing.out(Easing.ease),
  extrapolateRight: "clamp",
});

// Exit: easeIn feels natural
const exitOpacity = interpolate(frame, [60, 90], [1, 0], {
  easing: Easing.in(Easing.ease),
  extrapolateRight: "clamp",
});
```

**Applied**: TextOverlay uses spring for enter, easing for exit.

### Always Clamp Values
```tsx
// WRONG - values can exceed range
interpolate(frame, [0, 30], [0, 1]);

// CORRECT - values stay bounded
interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

**Applied**: All interpolations use clamp.

### Staggered Animations
Create visual hierarchy by delaying child elements:
```tsx
const item1Spring = spring({ frame: frame - 0, fps, ... });
const item2Spring = spring({ frame: frame - 15, fps, ... }); // 0.5s delay
const item3Spring = spring({ frame: frame - 30, fps, ... }); // 1.0s delay
```

**Applied**: Outro items animate in sequence.

---

## 3. Hackathon Video Best Practices

### First 8 Seconds Rule
Judges decide quickly. Your hook must appear immediately:
- Show the title/name
- State the value proposition
- Create visual interest

**Applied**: Intro is 8 seconds with immediate title animation.

### Video Structure
```
0:00-0:08   Hook (title + value prop)
0:08-0:20   Problem statement (optional, can be in recording)
0:20-3:50   Demo with annotations
3:50-4:30   CTA (live demo, github, contract)
```

**Applied**: Timeline follows this structure.

### Text Overlay Guidelines
- Use numbered steps (1, 2, 3...)
- Keep text short (< 10 words)
- High contrast backgrounds
- Don't obscure important UI elements
- Sync overlays to actual demo actions

**Applied**: TextOverlay has step numbers and clear styling.

### Recording Tips
1. **Warm up services** before recording
2. **Record 2 takes** - one clean, one safety
3. **Pre-generate assets** for slow API calls
4. **Hide sensitive data** (keys, seeds)
5. **Use minimal wallet balance**

---

## 4. Quality Settings

### Recommended Render Settings
```bash
# High quality (final export)
npx remotion render \
  --codec=h264 \
  --crf=18 \
  --color-space=bt709 \
  src/index.ts DemoVideo out/final.mp4

# Fast preview
npx remotion render \
  --codec=h264 \
  --crf=28 \
  --scale=0.5 \
  src/index.ts DemoVideo out/preview.mp4
```

### CRF Values (H.264)
| CRF | Quality | Use Case |
|-----|---------|----------|
| 18 | Excellent | Final export |
| 23 | Good | Default balance |
| 28 | Acceptable | Fast previews |
| 35+ | Poor | Not recommended |

### Color Space
Use `bt709` for accurate colors:
```bash
npx remotion render --color-space=bt709 ...
```

---

## 5. File Organization

### Recommended Structure
```
video-demo/
  public/
    demo-recording.mp4    # Screen recording
    assets/               # Images, fonts
  src/
    Root.tsx              # Composition registry
    index.ts              # Entry point
    DemoVideo.tsx         # Main composition
    Intro.tsx             # Opening sequence
    Outro.tsx             # Closing CTA
    components/           # Reusable pieces
      TextOverlay.tsx
      ProgressBar.tsx
```

### Asset Loading
```tsx
// CORRECT - use staticFile
import { staticFile } from "remotion";
<OffthreadVideo src={staticFile("demo-recording.mp4")} />

// WRONG - direct path
<video src="/demo-recording.mp4" />
```

---

## 6. Debugging

### Verbose Logging
```bash
npx remotion render --log=verbose ...
```
Shows frame-by-frame timing to identify slow frames.

### Performance Measurement
```tsx
// In component
console.time("expensive-operation");
// ... operation
console.timeEnd("expensive-operation");
```

### Flickering Issues
If animations flicker:
```bash
npx remotion render --concurrency=1 ...
```
Slower but deterministic.

---

## References

- [Remotion Performance Tips](https://www.remotion.dev/docs/performance)
- [Remotion Quality Guide](https://www.remotion.dev/docs/quality)
- [Remotion Easing API](https://www.remotion.dev/docs/easing)
- [Remotion interpolate()](https://www.remotion.dev/docs/interpolate)
- [Remotion spring()](https://www.remotion.dev/docs/spring)
- [Remotion staticFile()](https://www.remotion.dev/docs/staticfile)
- [Embedding Videos](https://www.remotion.dev/docs/videos/)
- [Hackathon Demo Tips](https://info.devpost.com/blog/6-tips-for-making-a-hackathon-demo-video)
- [Devpost Video Best Practices](https://help.devpost.com/article/84-video-making-best-practices)
- [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills)
- [Remotion LLM System Prompt](https://www.remotion.dev/docs/ai/system-prompt)
- [AI-friendly Docs](https://www.remotion.dev/docs/ai/)

---

## 7. AI Agent Workflow (Claude Code + Remotion)

### Mental Model

This is "agentic motion design" - creating videos as deterministic React code that AI can reliably generate and iterate on.

**Key Insight**: Remotion excels at UI-like compositions (terminals, app windows, dashboards) because the substrate is React + CSS and animation is frame-driven.

- **Remotion is React code rendered frame-by-frame** into media
- All animation must be **frame-driven** (`useCurrentFrame()`, `interpolate()`, `spring()`)
- Assets loaded via **render-safe primitives** (`<Img>`, `staticFile()`, `<OffthreadVideo>`)

### Make the Agent "Remotion-Literate"

Three layers of guardrails:
1. Install the [Remotion agent skill](https://www.remotion.dev/docs/ai/skills) (recommended by Remotion)
2. Feed the agent [Remotion's LLM system prompt](https://www.remotion.dev/docs/ai/system-prompt)
3. Point agent to [agent-friendly docs](https://www.remotion.dev/docs/ai/)

### Core Workflow Loop

#### Phase A: Specify Video as Scene Graph
```text
Format: (W x H, FPS, duration)
Scenes: Intro -> Main -> Outro
Assets: list files/URLs (public/ vs external)
Acceptance Tests: alignment, timings, loop behavior
```

#### Phase B: Implement with Deterministic Primitives
- Use `Sequence` / `Series` / `TransitionSeries` for ordering
- Use `interpolate()` / `spring()` to animate
- Avoid nondeterminism (`Math.random()`); use Remotion's `random('seed')` when needed

#### Phase C: Preview, Screenshot, Correct
When something is "almost right" (cursor position, spacing, timing):
1. Take a screenshot from Studio
2. Give the agent a **single, measurable correction**
   - e.g., "cursor center must coincide with Like button center"
   - e.g., "linger 12 frames before click; scale cursor 1.8x"

### Agent Prompt Template

```text
You are building a Remotion video as deterministic React code.

Goal:
- Create a {duration}s video at {fps}fps, {width}x{height}, exporting to MP4.

Scenes:
1) Intro (frames A-B): ...
2) Main (frames B-C): ...
3) Outro (frames C-D): ...

Visual style constraints:
- Typography: ...
- Colors: ...
- Spacing: ...
- Motion: keep simple, 1-2 focal animations at once.

Assets:
- public/profile.png (use staticFile())
- https://.../logo.svg

Rules:
- All animation must be driven by useCurrentFrame() + interpolate()/spring()
- Use <Img> for images to prevent flicker
- No Math.random(); use remotion random('seed') if needed

Acceptance tests:
- Text is not clipped at 1080p.
- Cursor clicks are centered on targets.
- Loop is seamless (no jump cuts).

Now implement, run only the minimum commands, and do not restart dev server if already running.
```

### Determinism Rules for Agents

| DO | DON'T |
|----|-------|
| `useCurrentFrame()` + `interpolate()` | CSS transitions/animations |
| `spring({ frame, fps, config })` | `Math.random()` |
| `random('seed')` for randomness | Async loading without `delayRender()` |
| `<Img>` for images | `<img>` directly |
| `staticFile('path')` | Direct path references |
| `<OffthreadVideo>` | `<Video>` for long clips |

---

## 8. Unintuitive Conclusions

1. **Motion design becomes prompting-and-QA, not keyframing** - The scarce skill shifts from After Effects craft to: writing an executable spec, selecting constraints, and debugging layout/timing deterministically.

2. **UI-first aesthetics dominate early AI motion design** - Agents are best at compositions that resemble "renderable web interfaces" (terminals, dashboards, app windows), because the underlying substrate is React + CSS.

3. **Precision feedback is the bottleneck, not generation** - You can get to 80% in minutes; the last 20% is screenshots, alignment, pixel positioning, easing curves, and timing corrections.

4. **Determinism is a creative constraint** - Anything nondeterministic (Math.random(), CSS transitions, async loading flicker) is a reliability risk in renders.

5. **Marketing throughput rises, but differentiation pressure rises faster** - If every solo operator can produce "good enough" motion graphics, advantage moves to concept quality, brand system consistency, and distribution.

6. **Content pipelines become software pipelines** - The natural next step is dataset-driven batch rendering (hundreds/thousands of variants) with CI, caching, and automated review.

---

## 9. Batch/Dataset Rendering

For scaling content production, use Remotion's [dataset-to-many-videos workflow](https://www.remotion.dev/docs/dataset-render):

```bash
# Single variant with props
npx remotion render HelloWorld out/video.mp4 --props='{"title":"Variant A"}'

# Script for batch rendering
for variant in variants/*.json; do
  npx remotion render HelloWorld "out/$(basename $variant .json).mp4" --props="$(cat $variant)"
done
```

This enables: A/B testing, localization, personalization at scale
