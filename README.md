# ammar-ai-video-studio
AI-powered video production studio for Arabic cinematic videos.

## Motion graphics studio (HyperFrames)

Motion-graphics production with [HyperFrames](https://hyperframes.heygen.com) lives in
`projects/`, `templates/` and `scripts/`. See **[STUDIO.md](STUDIO.md)** for setup, structure and workflow.

```bash
scripts/check-env.sh                              # Node 22+, FFmpeg, hyperframes doctor
scripts/new-project.sh my-video title-card-5s     # new project from a template
scripts/render.sh my-video delivery               # check + render + verify MP4
```
