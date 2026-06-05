/**
 * Intro - Opening sequence with animated title
 *
 * V2: Enhanced with particles and better animations
 */

import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  random,
} from "remotion";

/**
 * AnimatedParticles - Floating particle background
 */
const AnimatedParticles: React.FC<{ count?: number }> = ({ count = 50 }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const particles = Array.from({ length: count }, (_, i) => {
    const seed = i * 1000;
    const x = random(seed) * width;
    const y = random(seed + 1) * height;
    const size = 2 + random(seed + 2) * 4;
    const speed = 0.3 + random(seed + 3) * 0.7;
    const delay = random(seed + 4) * 100;

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
          background: "rgba(139, 92, 246, 0.4)",
          opacity: interpolate(yOffset, [0, height * 0.2, height * 0.8, height], [0, 1, 1, 0]),
        }}
      />
    );
  });

  return <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>{particles}</div>;
};

interface IntroProps {
  title: string;
  subtitle: string;
}

export const Intro: React.FC<IntroProps> = ({ title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Main title spring animation
  const titleSpring = spring({
    frame,
    fps,
    config: {
      damping: 12,
      stiffness: 80,
      mass: 0.8,
    },
  });

  // Subtitle with delay for staggered effect
  const subtitleSpring = spring({
    frame: frame - 15, // 0.5s delay
    fps,
    config: {
      damping: 15,
      stiffness: 100,
      mass: 0.5,
    },
  });

  // Badge appears last
  const badgeSpring = spring({
    frame: frame - 30, // 1s delay
    fps,
    config: {
      damping: 20,
      stiffness: 120,
      mass: 0.4,
    },
  });

  // Title animations
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(titleSpring, [0, 1], [60, 0], {
    extrapolateRight: "clamp",
  });
  const titleScale = interpolate(titleSpring, [0, 1], [0.9, 1], {
    extrapolateRight: "clamp",
  });

  // Subtitle animations
  const subtitleOpacity = interpolate(subtitleSpring, [0, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subtitleY = interpolate(subtitleSpring, [0, 1], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Badge animations
  const badgeOpacity = interpolate(badgeSpring, [0, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const badgeScale = interpolate(badgeSpring, [0, 1], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Background glow pulse (subtle, not GPU heavy)
  const glowPulse = interpolate(
    frame,
    [0, fps * 2, fps * 4],
    [0.3, 0.5, 0.3],
    {
      extrapolateRight: "extend",
    }
  );

  return (
    <AbsoluteFill
      style={{
        // PERFORMANCE: Use solid gradient, no blur
        background: "linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%)",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Animated particles */}
      <AnimatedParticles count={40} />

      {/* Background accent circles (no blur - performance) */}
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(139, 92, 246, ${glowPulse}) 0%, transparent 70%)`,
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%)",
          top: "30%",
          right: "20%",
        }}
      />

      {/* Main content */}
      <div
        style={{
          textAlign: "center",
          zIndex: 1,
          padding: 40,
        }}
      >
        {/* Title */}
        <h1
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px) scale(${titleScale})`,
            fontSize: 108,
            fontWeight: 800,
            color: "white",
            margin: 0,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
          }}
        >
          {title}
        </h1>

        {/* Subtitle */}
        <p
          style={{
            opacity: subtitleOpacity,
            transform: `translateY(${subtitleY}px)`,
            fontSize: 40,
            color: "#a78bfa",
            marginTop: 30,
            fontWeight: 500,
            letterSpacing: "0.01em",
          }}
        >
          {subtitle}
        </p>

        {/* Arc badge */}
        <div
          style={{
            opacity: badgeOpacity,
            transform: `scale(${badgeScale})`,
            marginTop: 60,
            display: "inline-flex",
            alignItems: "center",
            gap: 12,
            padding: "16px 36px",
            background: "rgba(255, 255, 255, 0.08)",
            borderRadius: 50,
            border: "1px solid rgba(255, 255, 255, 0.15)",
          }}
        >
          {/* Arc icon placeholder */}
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #8b5cf6, #3b82f6)",
            }}
          />
          <span style={{ color: "white", fontSize: 24, fontWeight: 500 }}>
            Built on Arc Blockchain
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
