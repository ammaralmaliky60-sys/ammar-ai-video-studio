# LOOK DEVELOPMENT — GATE 3A (Cinematic Visual Look)

**Status:** test frames rendered for review — **GATE 3A: AWAITING CINEMATIC VISUAL APPROVAL**.
**Scope:** three still frames only (A Mirror, B Fracture, C Courtroom). No film production, no long render, audio/script untouched.
**Animatic v0.1:** kept as a **timing & sync reference only** — its flat SVG look is NOT a visual reference (owner directive).

## 1. Decision (owner, 2026-11-24)
- Renderer for look-dev: **Blender 4.2.23 LTS — Cycles (CPU path tracing)**.
- Character: **MakeHuman / MPFB (CC0 output)** + CC0 suit; face hidden by lighting (back to camera, head in shadow).

## 2. Technical feasibility — honest assessment
| Need | Three.js on CPU (SwiftShader) | Blender Cycles on CPU (chosen for look-dev) |
|---|---|---|
| PBR materials | ✅ | ✅ |
| Real mirror reflections | ⚠️ approximate (planar reflector / cubemap) | ✅ path-traced |
| Volumetric light shafts | ⚠️ faked (cones / raymarch shader) | ✅ physical volume scattering |
| Optical depth of field | ⚠️ post-process approximation | ✅ physical aperture |
| Soft shadows / GI | ⚠️ limited | ✅ |
| Speed | fast enough for animation | **minutes per 1080×1920 frame** |

**Consequence for production (to be decided at GATE 3A/4):** full-film path tracing is not viable on this machine
(8,550 frames × several minutes ≈ weeks of CPU). The realistic route is **hybrid**:
1. Cycles-rendered **plates / layered passes** (background, mid-ground, foreground) for wide and slow shots,
2. **2.5D parallax + compositing in Remotion** (camera moves, light flicker, particles, typography),
3. **Three.js** only for shots that need true 3D motion (shard fly-through, scale, gavel→mirror), or short Cycles animated segments for hero moments,
4. or rendering the final animation on a machine with a GPU (owner's choice).

## 3. Pipeline used for the three frames
- Script: `src/lookdev/lookdev_frames.py` (deterministic: seeded RNG, fixed Cycles seed).
- `blender -b --python src/lookdev/lookdev_frames.py -- <A|B|C> <out.png> <scale%> <samples> <texdir>`
- Cycles CPU, adaptive sampling, OpenImageDenoise, AgX "Medium High Contrast", compositor Fog-Glow bloom, subtle lens dispersion and vignette.
- Character: MPFB base human (macro: gender 0.85, height 0.62), default rig, arms lowered from A-pose, CC0 suit `toigo_male_suit_3` re-shaded as dark wool (specular 0 — verified A/B test), skin kept in shadow.
- Light design per approved lighting script: P1 cold mirror with gold only in cracks; P2 court with motivated window shafts (one spot per window, sun direction) and gold back-light on the bench arch.
- KHAYBAR arch: frame/panel geometry from the brand arch proportions (semicircle over rectangle) — used for mirror, fracture frame and the arch behind the judge bench. **Official logo untouched.**

## 4. Assets & licences (downloaded to scratchpad, NOT committed)
| Asset | Source | Licence | Integrity |
|---|---|---|---|
| Blender 4.2.23 LTS (linux-x64) | download.blender.org | GPL (tool) | SHA-256 verified vs official .sha256 |
| MPFB 2.0.18 add-on | extensions.blender.org | GPL-3.0 (tool); generated humans CC0 | SHA-256 verified (`c075b3e9…2dad`) |
| suits01 asset pack (`toigo_male_suit_3`) | files.makehumancommunity.org | **CC0** | — |
| `black_walnut_veneer_01`, `dark_wooden_planks`, `volcanic_rock_tiles` (2K diff/rough/nor) | polyhaven.com | **CC0** | MD5 verified (Poly Haven API) |
| Gold, mirror, shard glass, wool, skin, paper, fog | procedural | project | — |

Not downloaded (judged unnecessary for this test): MakeHuman system assets (281 MB), hair packs (228 MB).
No paid service, no account, no purchase.

## 5. Known limitations of these test frames
- **Reference images (17): still not received** — frames follow the approved written direction only.
- Character: realistic proportions and clothing, but **no hair asset** (head kept as shadowed silhouette) and no hand/fabric simulation; close-ups would need a higher-grade asset.
- Frame B fracture is procedural (radial + concentric plane cuts), not a physics simulation; motion is suggested by motion blur and depth.
- Evidence papers are simple bent planes; no printed content.
- Render times on this 4-core CPU are listed in PROGRESS.md (measured).
