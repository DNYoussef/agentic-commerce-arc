/**
 * Outro - Closing sequence with CTA links
 *
 * BEST PRACTICES APPLIED:
 * - Staggered spring animations for items
 * - Clear CTA hierarchy (live demo first)
 * - Contract address displayed for credibility
 * - Hackathon attribution included
 * - No GPU-heavy effects
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
const AnimatedParticles: React.FC<{ count?: number; color?: string }> = ({
  count = 30,
  color = "rgba(139, 92, 246, 0.4)",
}) => {
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
          background: color,
          opacity: interpolate(yOffset, [0, height * 0.2, height * 0.8, height], [0, 1, 1, 0]),
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

interface OutroProps {
  githubUrl: string;
  contractAddress: string;
  liveUrl: string;
}

export const Outro: React.FC<OutroProps> = ({ githubUrl, contractAddress, liveUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title animation
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 80, mass: 0.8 },
  });

  // Staggered item animations
  const createItemSpring = (delay: number) => spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 100, mass: 0.5 },
  });

  const item1Spring = createItemSpring(15);
  const item2Spring = createItemSpring(25);
  const item3Spring = createItemSpring(35);
  const footerSpring = createItemSpring(50);

  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(titleSpring, [0, 1], [40, 0], { extrapolateRight: "clamp" });

  const createItemStyles = (springValue: number) => ({
    opacity: interpolate(springValue, [0, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    translateX: interpolate(springValue, [0, 1], [-30, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    scale: interpolate(springValue, [0, 1], [0.95, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  });

  const item1Styles = createItemStyles(item1Spring);
  const item2Styles = createItemStyles(item2Spring);
  const item3Styles = createItemStyles(item3Spring);
  const footerStyles = createItemStyles(footerSpring);

  // Pulsing glow for cards
  const glowIntensity = 0.3 + Math.sin(frame * 0.05) * 0.15;

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f3460 0%, #16213e 50%, #1a0a2e 100%)",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: 80,
      }}
    >
      {/* Background effects */}
      <GlowingOrbs />
      <AnimatedParticles count={35} />

      <div style={{ maxWidth: 1400, width: "100%", zIndex: 1 }}>
        {/* Title */}
        <h1
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            fontSize: 84,
            fontWeight: 800,
            color: "white",
            marginBottom: 60,
            textAlign: "center",
            textShadow: "0 0 40px rgba(139, 92, 246, 0.5)",
          }}
        >
          Try It Now
        </h1>

        {/* Links */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Primary CTA: Live Demo */}
          <div
            style={{
              opacity: item1Styles.opacity,
              transform: `translateX(${item1Styles.translateX}px) scale(${item1Styles.scale})`,
              background: "linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(139, 92, 246, 0.1))",
              padding: "28px 48px",
              borderRadius: 20,
              border: "2px solid rgba(139, 92, 246, 0.5)",
              boxShadow: `0 0 ${30 * glowIntensity}px rgba(139, 92, 246, ${glowIntensity}), inset 0 1px 0 rgba(255, 255, 255, 0.1)`,
              display: "flex",
              alignItems: "center",
              gap: 20,
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: "#8b5cf6",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 24,
              }}
            >
              🚀
            </div>
            <div>
              <span style={{ color: "#c4b5fd", fontSize: 20, display: "block" }}>
                Live Demo
              </span>
              <span style={{ color: "white", fontSize: 32, fontWeight: 600 }}>
                {liveUrl}
              </span>
            </div>
          </div>

          {/* GitHub */}
          <div
            style={{
              opacity: item2Styles.opacity,
              transform: `translateX(${item2Styles.translateX}px) scale(${item2Styles.scale})`,
              background: "rgba(255, 255, 255, 0.05)",
              padding: "24px 48px",
              borderRadius: 20,
              border: "1px solid rgba(255, 255, 255, 0.15)",
              display: "flex",
              alignItems: "center",
              gap: 20,
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: "#333",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 24,
              }}
            >
              📦
            </div>
            <div>
              <span style={{ color: "#94a3b8", fontSize: 20, display: "block" }}>
                Source Code
              </span>
              <span style={{ color: "white", fontSize: 28, fontWeight: 600 }}>
                {githubUrl}
              </span>
            </div>
          </div>

          {/* Contract Address */}
          <div
            style={{
              opacity: item3Styles.opacity,
              transform: `translateX(${item3Styles.translateX}px) scale(${item3Styles.scale})`,
              background: "rgba(34, 197, 94, 0.08)",
              padding: "24px 48px",
              borderRadius: 20,
              border: "1px solid rgba(34, 197, 94, 0.25)",
              display: "flex",
              alignItems: "center",
              gap: 20,
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: "rgba(34, 197, 94, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 24,
              }}
            >
              ⛓️
            </div>
            <div>
              <span style={{ color: "#86efac", fontSize: 20, display: "block" }}>
                Smart Contract (Arc Testnet)
              </span>
              <span
                style={{
                  color: "white",
                  fontSize: 22,
                  fontFamily: "ui-monospace, SFMono-Regular, monospace",
                  fontWeight: 500,
                }}
              >
                {contractAddress}
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            opacity: footerStyles.opacity,
            transform: `translateX(${footerStyles.translateX}px)`,
            marginTop: 60,
            textAlign: "center",
          }}
        >
          <p style={{ color: "#64748b", fontSize: 24, marginBottom: 8 }}>
            Built for the
          </p>
          <p style={{ color: "#94a3b8", fontSize: 32, fontWeight: 600 }}>
            lablab.ai Agentic Commerce on Arc Hackathon
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};
