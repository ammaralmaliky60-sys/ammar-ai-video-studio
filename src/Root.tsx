import React from "react";
import { Composition } from "remotion";
import { FPS, FRAME } from "./brand/tokens";
import { KhaybarOutro, KhaybarOutroProps, outroDefaults } from "./compositions/KhaybarOutro";
import { KhaybarLogo } from "./components/KhaybarLogo";

const LogoStill: React.FC = () => <KhaybarLogo size={1000} reveal={{ metallic: 1 }} />;

export const Root: React.FC = () => (
  <>
    <Composition
      id="KhaybarOutro"
      component={KhaybarOutro}
      width={FRAME.width}
      height={FRAME.height}
      fps={FPS}
      durationInFrames={Math.round(outroDefaults.totalSeconds * FPS)}
      defaultProps={outroDefaults}
      calculateMetadata={({ props }: { props: KhaybarOutroProps }) => ({
        durationInFrames: Math.round(props.totalSeconds * FPS),
      })}
    />
    <Composition id="KhaybarLogoCinematic" component={LogoStill} width={1000} height={1000} fps={FPS} durationInFrames={1} />
  </>
);
