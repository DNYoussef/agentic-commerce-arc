import { Composition } from "remotion";
import { DemoVideo } from "./DemoVideo";
import { Intro } from "./Intro";
import { Outro } from "./Outro";

// Video configuration
const FPS = 30;
const DURATION_SECONDS = 58; // ~1 minute demo

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Full demo video composition */}
      <Composition
        id="DemoVideo"
        component={DemoVideo}
        durationInFrames={DURATION_SECONDS * FPS}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Agentic Commerce on Arc",
        }}
      />

      {/* Standalone intro (10 seconds) */}
      <Composition
        id="Intro"
        component={Intro}
        durationInFrames={10 * FPS}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Agentic Commerce on Arc",
          subtitle: "AI Agents That Shop, Create, and Trade for You",
        }}
      />

      {/* Standalone outro (15 seconds) */}
      <Composition
        id="Outro"
        component={Outro}
        durationInFrames={15 * FPS}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          githubUrl: "github.com/DNYoussef/agentic-commerce-arc",
          contractAddress: "0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171",
          liveUrl: "frontend-production-dd6f.up.railway.app",
        }}
      />
    </>
  );
};
