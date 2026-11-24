import React from "react";
import { Composition } from "remotion";
import { FPS, FRAME } from "./brand/tokens";
import { TypographyTest } from "./animatic/TypographyTest";
import { Animatic, AnimaticProps } from "./animatic/Animatic";
import shotList from "../docs/SHOT_LIST.json";

const animaticDefaults: AnimaticProps = { showSafeZones: true, showOverlays: true };
/** Opening preview = hook → mirror portal → courtroom title (shots S01_01–S01_03). */
const OPENING_FRAMES = shotList.shots.find((s) => s.id === "S01_03")!.end_frame;

export const Root: React.FC = () => (
  <>
    <Composition id="AnimaticFull" component={Animatic} width={FRAME.width} height={FRAME.height} fps={FPS}
      durationInFrames={shotList.total_frames} defaultProps={animaticDefaults} />
    <Composition id="AnimaticOpening" component={Animatic} width={FRAME.width} height={FRAME.height} fps={FPS}
      durationInFrames={OPENING_FRAMES} defaultProps={animaticDefaults} />
    <Composition id="TypographyTest" component={TypographyTest} width={FRAME.width} height={FRAME.height} fps={FPS} durationInFrames={1} />
  </>
);
