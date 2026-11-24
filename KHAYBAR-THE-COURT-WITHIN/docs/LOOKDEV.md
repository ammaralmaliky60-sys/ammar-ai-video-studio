# LOOK DEVELOPMENT — GATE 3A (Cinematic Visual Look)

**Status:** V3 frames rendered — **GATE 3A — V3 VISUAL REVIEW / AWAITING USER APPROVAL**. V1/V2 = development history only (owner).
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


---
## V2 — Reference-driven refinement (REF_01–REF_20 + REFERENCE_GUIDE.md)
Script: `src/lookdev/lookdev_frames_v2.py` (V1 script kept unchanged for comparison).
Outputs: `previews/lookdev/frame-{A,B,C}-V2-1080x1920.png`, comparison `previews/lookdev/v1-vs-v2-comparison.png` (A1 A2 B1 B2 C1 C2).

| Frame | References used | What changed | Remaining weaknesses (honest) |
|---|---|---|---|
| A Mirror | REF_18, REF_06, REF_01, REF_05 | Figure centred from behind; single cold top shaft → long shadow toward camera; polished stone floor; receding basalt arches + walnut wainscot replace flat orange wall; warm kick + warm fog + teal hidden from reflections → **gold frame no longer green**; CC0 short dark hair | Mirror reflection still reads as a soft grey panel (reflection of the figure weak); background arches mostly hidden behind the mirror; overall still dark for phone screens |
| B Fracture | REF_15, REF_16 | Glass with real thickness (refractive edge material on rims), irregular (non-tangent) concentric cuts, bright shard edges reflecting a lit front environment, out-of-focus foreground shards, glow reduced to a point source behind the cracks | Background now very dark; warm point glow reads a little like fire; frame left edge still picks up teal; composition busier than V1 |
| C Courtroom | REF_02, REF_03, REF_20/07, REF_09, REF_12 | Tall arched window behind the bench (judge backlit), stepped judicial platform, panelled bench, fluted columns with base/capital, wainscot, ceiling beams, chandeliers, pews with backs, balustered dock, larger papers inside shafts, higher camera (less floor) | Floor still ~35% of frame; papers small at phone scale; witness area dark; materials repeat (same basalt/walnut set) |

**Assets added for V2:** MakeHuman `hair01` pack — **all 25 items CC0** (verified on the pack page before download), 227.8 MB, used item `culturalibre_hair_02` (strand alpha kept, colour tinted near-black). Not committed.

## Performance benchmark (measured on this 4-core CPU, no GPU)
| Test | Result |
|---|---|
| Cycles 1080×1920, 64 spp + OIDN (V2 final) | A 372 s · B 413 s · C 468 s (render 7:37) · peak RAM 249–317 MB |
| Cycles 540×960, 32 spp (preview) | A 44.5 s · C 59.6 s render (47.6 / 70.3 s incl. scene build) · peak 137–204 MB |
| Cycles 270×480, 16 spp (look tests) | 11–20 s |
| Scene/asset build (MPFB human + suit + hair, textures) | < 3 s of the total (log: sync at 0.68 s) |
| **Blender Eevee** | ❌ **not available**: `libEGL.so.1` missing, no GPU — render aborts (exit 134). Not installed further. |
| Remotion 2.5D parallax of a Cycles plate (3 layers + depth blur + 120 particles), 1080×1920 | 150 frames in 48 s (≈0.3 s/frame incl. ~15 s bundling) |
| Remotion SVG animatic 540×960 (Phase 3) | 8,550 frames in 286 s |

### Production estimate (planning only — derived from the measurements above)
- **Full-film Cycles at 1080×1920:** 8,550 × ~7 min ≈ **~41 days** → rejected.
- **Hybrid:** ~56 shots × ~2 plates/passes × ~7 min ≈ **~13 h** of plates + Remotion compositing of the whole film ≈ **~45 min** + re-renders.
- **Animated hero moments in Cycles** (character/shards/gavel actually moving): ~45–60 s/frame at 540×960 → 10 s of motion ≈ **4–5 h** at preview res, far more at 1080. → hero motion must come from **Three.js real-time POC** (not yet measured for quality) or very short Cycles segments.
- **Not yet demonstrated:** Three.js quality/speed for the hero shots, depth-pass parallax on real plates, character animation. These are the GATE 4 POCs.


---
## V3 — Targeted refinement (owner directive "GATE 3A — V3")
Script: `src/lookdev/lookdev_frames_v3.py` (V1/V2 scripts unchanged). Outputs: `previews/lookdev/frame-{A,B,C}-V3-1080x1920.png`,
comparison `previews/lookdev/v1-v2-v3-comparison.png` (A1 A2 A3 · B1 B2 B3 · C1 C2 C3), memory vignettes `previews/lookdev/memories/M1–M3.png`.
Workflow followed: all composition tests at 540×960 (16 spp, 25–40 s each); 1080×1920 only after approval of the low-res look.

| Frame | 1080×1920 render (64 spp) | Changes vs V2 | Remaining problems (unvarnished) |
|---|---|---|---|
| A Mirror | **340 s**, peak 252 MB | Real mirror: brighter silvered glass reflects a lit wall *behind the camera* with a warm KHAYBAR doorway → the figure's front appears as a **dark silhouette against light** (faceless by design, no light on the face); 3/4 camera so reflection perspective reads; gold/teal rim lights separate figure/mirror; visible side arcades with fluted columns; lights hidden from camera | Upper third very dark on a phone; arcades still read mainly as dark shapes; reflected silhouette is slightly small; floor stones a bit too uniform |
| B Shattered Memories | **367 s**, peak 230 MB | Rebuilt: three large hero shards carry readable CH02 memories (M1 hurtful word, M2 silence, M3 backbiting with an empty chair) rendered as separate Cycles vignettes and set behind real coated glass with refractive rims; debris reduced to support; foreground defocused shards; fire-like orange glow removed (ivory light only in the background cracks) | **Glass still reads more like printed cards than thick glass** (reflections/edge glints weak); background broken mirror shows a pale panel; debris almost invisible; M2's meaning is the least clear; vignette poses are stiff |
| C Courtroom | **464 s**, peak 317 MB | Camera closer and tilted up (visible floor ≈ 20–25 %, partly covered by pews); bench, window arch and two flanking arches dominate; six texture variants with procedural grime (two walnut, two stone, panel, floor) break repetition; larger papers in mid-ground shafts; bench face light; identities kept hidden | Floor still slightly above the 15–20 % target; papers remain small at phone scale; pews in the foreground look plain/boxy; chandeliers simple |

**Memory vignettes (M1–M3):** 720×900, 32 spp, 44–73 s each; MPFB humans, back/rim light only (all faces in shadow).

### Benchmark update
Measured V3 finals 340–464 s/frame at 1080×1920 (unchanged range vs V2: 372–468 s). The production estimate in the V2 section is unchanged:
hybrid ≈ ~13 h of Cycles plates + ~45 min Remotion compositing; hero motion still requires the Three.js / short-Cycles POCs (not measured yet).
