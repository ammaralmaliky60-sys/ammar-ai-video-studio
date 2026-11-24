/**
 * POC 04 — Gavel → Mirror of Insight (hybrid test).
 * Layer 1: Cycles background plate (open space after the collapse) — previews/poc/P4BG plate.
 * Layer 2: Three.js (via @remotion/three): walnut/gold gavel → golden particles → KHAYBAR-arch mirror.
 * Layer 3: Remotion compositing (glow, grade, vignette).
 * Fully frame-driven & seeded (no Math.random / Date / timers).
 */
import React, { useMemo } from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";

const N = 4200;
const MS = 0.72, MY = -0.5, GS = 0.62;
const GAVEL_EULER = new THREE.Euler(0.25, 1.1, -0.35);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const e = Easing.bezier(0.45, 0, 0.2, 1);

/** Points on the gavel surface: head (cylinder along X) + handle (cylinder along -Y) + gold ring. */
const gavelPoints = (): Float32Array => {
  const p = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    const u = random(`g${i}`), a = random(`ga${i}`) * Math.PI * 2;
    let x: number, y: number, z: number;
    if (u < 0.62) { x = (random(`gx${i}`) - 0.5) * 0.72; y = Math.cos(a) * 0.17; z = Math.sin(a) * 0.17; }
    else if (u < 0.92) { x = Math.cos(a) * 0.045; y = -0.17 - random(`gy${i}`) * 0.95; z = Math.sin(a) * 0.045; }
    else { x = (random(`gr${i}`) < 0.5 ? -0.2 : 0.2) + (random(`gq${i}`) - 0.5) * 0.04; y = Math.cos(a) * 0.185; z = Math.sin(a) * 0.185; }
    const v = new THREE.Vector3(x, y + 0.35, z).applyEuler(GAVEL_EULER).multiplyScalar(GS);
    p.set([v.x, v.y + 0.1, v.z], i * 3);
  }
  return p;
};

/** Points on the KHAYBAR arch mirror: dense on the frame outline, sparse over the glass. */
const mirrorPoints = (): Float32Array => {
  const p = new Float32Array(N * 3), w = 0.9, h = 1.75, r = w / 2;
  for (let i = 0; i < N; i++) {
    const u = random(`m${i}`);
    let x: number, y: number;
    if (u < 0.7) {
      const t = random(`mt${i}`), straight = (h - r) * 2, arc = Math.PI * r, L = straight + arc, d = t * L;
      if (d < h - r) { x = -r; y = d; } else if (d < h - r + arc) { const a = Math.PI - (d - (h - r)) / r; x = Math.cos(a) * r; y = h - r + Math.sin(a) * r; } else { x = r; y = h - r - (d - (h - r + arc)); }
      x += (random(`mj${i}`) - 0.5) * 0.03; y += (random(`mk${i}`) - 0.5) * 0.03;
    } else {
      x = (random(`mx${i}`) - 0.5) * w * 0.92; y = random(`my${i}`) * (h - r);
      if (random(`mz${i}`) < 0.4) { const a = random(`ma${i}`) * Math.PI; const rr = random(`mr${i}`) * r * 0.92; x = Math.cos(a) * rr; y = h - r + Math.sin(a) * rr; }
    }
    p.set([x * MS, y * MS + MY, (random(`md${i}`) - 0.5) * 0.02], i * 3);
  }
  return p;
};

const archShape = (w: number, h: number) => {
  const r = w / 2, s = new THREE.Shape();
  s.moveTo(-r, 0); s.lineTo(-r, h - r); s.absarc(0, h - r, r, Math.PI, 0, true); s.lineTo(r, 0); s.lineTo(-r, 0);
  return s;
};

const Scene: React.FC<{ f: number }> = ({ f }) => {
  const g = useMemo(gavelPoints, []), m = useMemo(mirrorPoints, []);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const mesh = React.useRef<THREE.InstancedMesh>(null);

  // timeline (frames): 0–34 gavel; 30–52 dissolve; 48–112 travel/swirl; 104–126 mirror resolves; hold
  const dissolve = interpolate(f, [30, 52], [0, 1], { ...clamp, easing: e });
  const travel = interpolate(f, [48, 112], [0, 1], { ...clamp, easing: e });
  const resolve = interpolate(f, [104, 126], [0, 1], { ...clamp, easing: e });
  const rotY = interpolate(f, [0, 40], [0.6, 1.1], { ...clamp, easing: e });

  React.useLayoutEffect(() => {
    if (!mesh.current) return;
    for (let i = 0; i < N; i++) {
      const k = i * 3, t = interpolate(travel, [random(`d${i}`) * 0.25, 0.75 + random(`d${i}`) * 0.25], [0, 1], clamp);
      const swirl = Math.sin(t * Math.PI) * (0.35 + random(`s${i}`) * 0.4), ang = t * 5 + random(`sa${i}`) * 6.28;
      const x = g[k] + (m[k] - g[k]) * t + Math.cos(ang) * swirl * 0.6;
      const y = g[k + 1] + (m[k + 1] - g[k + 1]) * t + Math.sin(t * Math.PI) * 0.25;
      const z = g[k + 2] + (m[k + 2] - g[k + 2]) * t + Math.sin(ang) * swirl * 0.6;
      dummy.position.set(x, y, z);
      const sc = (0.006 + random(`z${i}`) * 0.008) * (dissolve > 0 ? 1 : 0) * (1 - resolve * 0.75);
      dummy.scale.setScalar(sc); dummy.updateMatrix(); mesh.current.setMatrixAt(i, dummy.matrix);
    }
    mesh.current.instanceMatrix.needsUpdate = true;
  }, [f, travel, dissolve, resolve, g, m, dummy]);

  const shape = useMemo(() => archShape(0.9, 1.75), []);
  const inner = useMemo(() => archShape(0.84, 1.72), []);
  const frameShape = useMemo(() => { const s = archShape(0.98, 1.8); s.holes.push(new THREE.Path(inner.getPoints(48).reverse())); return s; }, [inner]);

  return (
    <>
      <ambientLight intensity={0.35} color="#bcd6dc" />
      <directionalLight position={[2, 3, 4]} intensity={2.2} color="#f4e9d3" />
      <pointLight position={[-2, 1, 2]} intensity={6} color="#D4AA61" distance={8} />
      {/* gavel: walnut head + handle + aged-gold ring, fades as it dissolves */}
      <group rotation={[0.25, rotY, -0.35]} position={[0, 0.1, 0]} scale={GS} visible={dissolve < 0.999}>
        <mesh position={[0, 0.35, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.17, 0.17, 0.72, 48]} />
          <meshStandardMaterial color="#3a2416" roughness={0.55} metalness={0} transparent opacity={1 - dissolve} />
        </mesh>
        {[-0.2, 0.2].map((x) => (
          <mesh key={x} position={[x, 0.35, 0]} rotation={[0, 0, Math.PI / 2]}>
            <torusGeometry args={[0.172, 0.018, 16, 64]} />
            <meshStandardMaterial color="#C9A05A" roughness={0.3} metalness={1} transparent opacity={1 - dissolve} />
          </mesh>
        ))}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.045, 0.05, 0.95, 32]} />
          <meshStandardMaterial color="#3a2416" roughness={0.6} transparent opacity={1 - dissolve} />
        </mesh>
      </group>
      <instancedMesh ref={mesh} args={[undefined, undefined, N]}>
          <sphereGeometry args={[1, 6, 6]} />
          <meshBasicMaterial color="#F2DCA6" toneMapped={false} blending={THREE.AdditiveBlending} transparent opacity={0.85} depthWrite={false} />
        </instancedMesh>
      {/* Mirror of Insight: aged-gold KHAYBAR arch frame + smoked reflective glass, resolves from the particles */}
      <group position={[0, MY, 0]} scale={MS} rotation={[0, interpolate(f, [104, 150], [-0.35, 0], { ...clamp, easing: e }), 0]}>
        <mesh position={[0, 0, -0.01]}>
          <shapeGeometry args={[shape, 48]} />
          <meshBasicMaterial color="#e9e2cf" transparent opacity={resolve * 0.42} toneMapped={false} />
        </mesh>
        <mesh>
          <extrudeGeometry args={[frameShape, { depth: 0.05, bevelEnabled: true, bevelSize: 0.01, bevelThickness: 0.01, curveSegments: 48 }]} />
          <meshStandardMaterial color="#C9A05A" metalness={1} roughness={0.28} transparent opacity={resolve} />
        </mesh>
      </group>
    </>
  );
};

export const GavelToMirror: React.FC = () => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const glow = interpolate(f, [30, 70, 120, 150], [0, 0.55, 0.35, 0.2], clamp);
  return (
    <AbsoluteFill style={{ background: "#071F26" }}>
      <Img src={staticFile("poc/P4BG.png")} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover",
        transform: `scale(${1.04 + f * 0.0004})` }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 48%, rgba(242,220,166,${glow}) 0%, rgba(242,220,166,0) 45%)`, mixBlendMode: "screen" }} />
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0.2, 3.4], fov: 38 }} gl={{ antialias: true, preserveDrawingBuffer: true }}
        style={{ position: "absolute" }}>
        <Scene f={f} />
      </ThreeCanvas>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};
