# KHAYBAR — Phase 1: Reference analysis & logo architecture

Status: **awaiting owner selection (A / B / C)**.

## Reference
- `references/khaybar-original.mp4` — original identity video (1080×1920, 30fps, 5.1s, no audio).
- `references/frames/` — extracted frames (`f_<seconds>.png`, `contact.png`, `original-mark-crop.png`).

Key finding: the three turquoise diamonds are the letter dots of «خيبر» (ي = 2, ب = 1);
the kha dot is an ivory diamond. All proposals keep them in their orthographic position.

## Deliverables
| Path | Content |
|---|---|
| `brand/logo/phase-1/khaybar-proposal-{A,B,C}.svg` | Full proposals, pure vector, Flat Official Gold |
| `brand/logo/phase-1/khaybar-proposal-{A,B,C}-small.svg` | Small-size variants (no dots/pattern, enlarged word) |
| `brand/logo/phase-1/wordmark-R0-reconstruction.svg` | Vector reconstruction of the original wordmark (shared by all proposals) |
| `brand/logo/phase-1/proposals-meta.json` | Measured geometry per proposal |
| `exports/phase-1/` | PNG renders at 1000px and 48/64/128/256 |
| `showcase/phase-1/index.html` | RTL comparison page |

## Regenerate
```bash
pip install shapely
python3 scripts/phase1_logo.py              # SVGs + meta
python3 scripts/build_showcase_phase1.py    # comparison page
node scripts/render_svgs.js exports/phase-1 1000 brand/logo/phase-1/khaybar-proposal-A.svg
```
Then open `showcase/phase-1/index.html` in a browser.

## Open decisions
1. Proposal A, B or C.
2. Eight-point star: crown (A, C), keystone (B), or removed.
3. Remove the small turquoise diamond under the star (done in all three).
4. Word colour: ivory (as original) or gold.
