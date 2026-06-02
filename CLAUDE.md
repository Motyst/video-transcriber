# Video Transcriber

Personal tool: transcribe video/audio from URLs (YouTube, social media) and local files.

## Stack
- Python 3.10+
- `faster-whisper` — local Whisper transcription (no API cost)
- `yt-dlp` — URL download (YouTube, TikTok, Instagram, Twitter/X, etc.)
- `FastAPI` + `uvicorn` — web UI backend
- `Click` — CLI
- `ffmpeg` — system binary for audio extraction (must be installed separately)

## Entry Points

**CLI (default):**
```bash
python cli.py <source> [options]

# Examples
python cli.py https://youtube.com/watch?v=xxx
python cli.py video.mp4
python cli.py /path/to/folder/          # batch: all media files recursively
python cli.py vid1.mp4 vid2.mp4 -m medium -f srt
```

**Web UI:**
```bash
python web/app.py        # → http://localhost:8000
```

## CLI Options
| Flag | Default | Options |
|------|---------|---------|
| `-m/--model` | `base` | tiny, base, small, medium, large-v3 |
| `-f/--format` | `txt` | txt, srt |
| `-l/--language` | auto | en, es, fr, de, it, pt, ru, zh, ja, ar, lv… |
| `-o/--output` | same as input | path to output directory |

## Architecture
```
transcriber/
  core.py        — main logic: route input → audio → Whisper → format
  downloader.py  — yt-dlp wrapper (URL → wav)
  formatter.py   — txt / SRT formatters
web/
  app.py         — FastAPI: POST /transcribe, GET /status/{id} (SSE)
  static/
    index.html   — single-page UI
cli.py           — Click CLI entry point
```

## System Requirement
ffmpeg must be on PATH. Install:
- Windows: `winget install ffmpeg` or download from https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg`

## Model Size Guide
| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| tiny | fastest | lowest | ~1 GB |
| base | fast | decent | ~1 GB |
| small | moderate | good | ~2 GB |
| medium | slow | very good | ~5 GB |
| large-v3 | slowest | best | ~10 GB |
