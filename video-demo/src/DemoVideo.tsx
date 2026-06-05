/**
 * DemoVideo - Main composition for ARC hackathon demo
 *
 * V2: Fixed cropping, added particles, improved animations
 */

import {
  AbsoluteFill,
  Sequence,
  Img,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  random,
} from "remotion";
import { Intro } from "./Intro";
import { Outro } from "./Outro";

interface DemoVideoProps {
  title: string;
}

/**
 * AnimatedParticles - Floating particle background
 */
const AnimatedParticles: React.FC<{ count?: number; color?: string }> = ({
  count = 30,
  color = "rgba(139, 92, 246, 0.4)",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();

  const particles = Array.from({ length: count }, (_, i) => {
    const seed = i * 1000;
    const x = random(seed) * width;
    const y = random(seed + 1) * height;
    const size = 2 + random(seed + 2) * 4;
    const speed = 0.3 + random(seed + 3) * 0.7;
    const delay = random(seed + 4) * 100;

    // Float upward with slight horizontal drift
    const yOffset = ((frame + delay) * speed) % (height + 100);
    const xDrift = Math.sin((frame + delay) * 0.02) * 30;

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: x + xDrift,
          top: height - yOffset,
          width: size,
          height: size,
          borderRadius: "50%",
          background: color,
          opacity: interpolate(
            yOffset,
            [0, height * 0.2, height * 0.8, height],
            [0, 1, 1, 0]
          ),
        }}
      />
    );
  });

  return <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>{particles}</div>;
};

/**
 * GlowingOrbs - Animated background orbs
 */
const GlowingOrbs: React.FC = () => {
  const frame = useCurrentFrame();

  const orbs = [
    { x: "20%", y: "30%", size: 400, color: "rgba(139, 92, 246, 0.15)", speed: 0.5 },
    { x: "80%", y: "70%", size: 350, color: "rgba(59, 130, 246, 0.12)", speed: 0.7 },
    { x: "50%", y: "50%", size: 500, color: "rgba(139, 92, 246, 0.08)", speed: 0.3 },
  ];

  return (
    <>
      {orbs.map((orb, i) => {
        const pulse = 1 + Math.sin(frame * 0.02 * orb.speed) * 0.1;
        const drift = Math.sin(frame * 0.01 * orb.speed) * 20;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: orb.x,
              top: orb.y,
              width: orb.size * pulse,
              height: orb.size * pulse,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${orb.color} 0%, transparent 70%)`,
              transform: `translate(-50%, -50%) translate(${drift}px, ${drift * 0.5}px)`,
            }}
          />
        );
      })}
    </>
  );
};

/**
 * ScreenshotScene - Full screenshot display with subtle animation
 */
const ScreenshotScene: React.FC<{
  src: string;
  zoomStart?: number;
  zoomEnd?: number;
}> = ({ src, zoomStart = 1, zoomEnd = 1.02 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Subtle Ken Burns zoom
  const scale = interpolate(frame, [0, durationInFrames], [zoomStart, zoomEnd], {
    extrapolateRight: "clamp",
  });

  // Fade in with spring
  const fadeSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 80, mass: 0.5 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      <GlowingOrbs />
      <AnimatedParticles count={20} />

      {/* Screenshot container - centered with padding */}
      <div
        style={{
          position: "absolute",
          inset: 40,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          opacity: fadeSpring,
        }}
      >
        {/* Screenshot with border glow */}
        <div
          style={{
            position: "relative",
            maxWidth: "95%",
            maxHeight: "95%",
            borderRadius: 16,
            overflow: "hidden",
            boxShadow: "0 0 60px rgba(139, 92, 246, 0.3), 0 20px 60px rgba(0, 0, 0, 0.5)",
            border: "2px solid rgba(139, 92, 246, 0.4)",
            transform: `scale(${scale})`,
          }}
        >
          <Img
            src={src}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
              display: "block",
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * TextOverlay - Animated annotation with glow
 */
const TextOverlay: React.FC<{
  text: string;
  position?: "top" | "bottom";
  stepNumber?: number;
  delay?: number;
}> = ({ text, position = "bottom", stepNumber, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enterSpring = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 80, mass: 0.5 },
  });

  const opacity = interpolate(enterSpring, [0, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(enterSpring, [0, 1], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(enterSpring, [0, 1], [0.9, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        [position]: 60,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
      }}
    >
      <div
        style={{
          background: "linear-gradient(135deg, rgba(20, 10, 40, 0.95), rgba(15, 15, 30, 0.95))",
          padding: "24px 56px",
          borderRadius: 20,
          border: "2px solid rgba(139, 92, 246, 0.5)",
          boxShadow: "0 0 40px rgba(139, 92, 246, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
          display: "flex",
          alignItems: "center",
          gap: 20,
        }}
      >
        {stepNumber && (
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #8b5cf6, #6366f1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: 32,
              fontWeight: 700,
              fontFamily: "system-ui, -apple-system, sans-serif",
              boxShadow: "0 4px 20px rgba(139, 92, 246, 0.5)",
            }}
          >
            {stepNumber}
          </div>
        )}
        <span
          style={{
            color: "white",
            fontSize: 48,
            fontWeight: 600,
            fontFamily: "system-ui, -apple-system, sans-serif",
            textShadow: "0 2px 10px rgba(0, 0, 0, 0.5)",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};

/**
 * FeatureCard - Individual animated feature
 */
const FeatureCard: React.FC<{
  icon: string;
  text: string;
  index: number;
}> = ({ icon, text, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const delay = 20 + index * 20;
  const featureSpring = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 60, mass: 0.8 },
  });

  const opacity = interpolate(featureSpring, [0, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateX = interpolate(featureSpring, [0, 1], [-100, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(featureSpring, [0, 1], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtle glow pulse
  const glowIntensity = 0.3 + Math.sin(frame * 0.05 + index) * 0.1;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 28,
        opacity,
        transform: `translateX(${translateX}px) scale(${scale})`,
        background: "linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.05))",
        padding: "28px 48px",
        borderRadius: 20,
        border: "1px solid rgba(139, 92, 246, 0.4)",
        boxShadow: `0 0 ${30 * glowIntensity}px rgba(139, 92, 246, ${glowIntensity})`,
        minWidth: 700,
      }}
    >
      <div
        style={{
          width: 64,
          height: 64,
          borderRadius: 16,
          background: "linear-gradient(135deg, #8b5cf6, #6366f1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontSize: 36,
          fontWeight: 700,
          boxShadow: "0 4px 20px rgba(139, 92, 246, 0.4)",
        }}
      >
        {icon}
      </div>
      <span style={{ color: "white", fontSize: 36, fontWeight: 500 }}>
        {text}
      </span>
    </div>
  );
};

/**
 * FeatureShowcase - Enhanced "How It Works" section
 */
const FeatureShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80, mass: 0.6 },
  });

  const features = [
    { icon: "1", text: "Describe products in natural language" },
    { icon: "2", text: "AI generates unique images with FLUX" },
    { icon: "3", text: "Purchase through SimpleEscrow on Arc" },
    { icon: "4", text: "Trade or redeem for physical goods" },
  ];

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0f1a3a 100%)",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <GlowingOrbs />
      <AnimatedParticles count={40} color="rgba(139, 92, 246, 0.3)" />

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
        }}
      >
        {/* Title */}
        <h2
          style={{
            fontSize: 80,
            fontWeight: 800,
            color: "white",
            marginBottom: 60,
            opacity: titleSpring,
            transform: `translateY(${interpolate(titleSpring, [0, 1], [30, 0])}px)`,
            textShadow: "0 0 40px rgba(139, 92, 246, 0.5)",
          }}
        >
          How It Works
        </h2>

        {/* Feature cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} index={index} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * ProgressBar - Animated progress indicator
 */
const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 4,
        background: "rgba(255, 255, 255, 0.1)",
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          background: "linear-gradient(90deg, #8b5cf6, #a78bfa, #c4b5fd)",
          boxShadow: "0 0 20px rgba(139, 92, 246, 0.8)",
        }}
      />
    </div>
  );
};

export const DemoVideo: React.FC<DemoVideoProps> = ({ title }) => {
  const FPS = 30;

  /**
   * TIMELINE (~60 seconds)
   * 0:00-0:06  Intro
   * 0:06-0:13  Welcome screen
   * 0:13-0:20  Typing prompt
   * 0:20-0:30  AI Result
   * 0:30-0:42  Feature showcase
   * 0:42-0:58  Outro
   */

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      {/* Background music */}
      <Audio src={staticFile("music.mp3")} volume={0.4} />

      {/* INTRO: 0-6 seconds */}
      <Sequence from={0} durationInFrames={6 * FPS}>
        <Intro
          title="Agentic Commerce"
          subtitle="AI Agents That Shop, Create, and Trade for You"
        />
      </Sequence>

      {/* SCENE 1: Welcome Screen - 6-13 seconds */}
      <Sequence from={6 * FPS} durationInFrames={7 * FPS}>
        <ScreenshotScene src={staticFile("welcome.PNG")} zoomStart={1} zoomEnd={1.015} />
        <TextOverlay text="Describe the product you want" stepNumber={1} delay={20} />
      </Sequence>

      {/* SCENE 2: Typing Prompt - 13-20 seconds */}
      <Sequence from={13 * FPS} durationInFrames={7 * FPS}>
        <ScreenshotScene src={staticFile("typing.PNG")} zoomStart={1} zoomEnd={1.015} />
        <TextOverlay text="Natural language input" stepNumber={2} delay={20} />
      </Sequence>

      {/* SCENE 3: AI Generated Result - 20-30 seconds */}
      <Sequence from={20 * FPS} durationInFrames={10 * FPS}>
        <ScreenshotScene src={staticFile("result.PNG")} zoomStart={1} zoomEnd={1.02} />
        <TextOverlay text="AI generates unique product" stepNumber={3} delay={20} />
      </Sequence>

      {/* FEATURE SHOWCASE - 30-42 seconds */}
      <Sequence from={30 * FPS} durationInFrames={12 * FPS}>
        <FeatureShowcase />
      </Sequence>

      {/* OUTRO: 42-58 seconds */}
      <Sequence from={42 * FPS} durationInFrames={16 * FPS}>
        <Outro
          githubUrl="github.com/DNYoussef/agentic-commerce-arc"
          contractAddress="0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171"
          liveUrl="frontend-production-dd6f.up.railway.app"
        />
      </Sequence>

      {/* Progress bar */}
      <ProgressBar />
    </AbsoluteFill>
  );
};
