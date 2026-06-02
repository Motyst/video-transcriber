# Video Transcriber

Transcribe video/audio from URLs (YouTube, TikTok, Instagram, X/Twitter) and local files. Runs fully local — no API costs.

## Requirements

- Python 3.10+
- ffmpeg on PATH

```powershell
winget install ffmpeg
pip install -r requirements.txt
```

## Usage

### Web UI

```bash
python web/app.py
```

Open `http://localhost:8000` — paste a URL or upload files, pick model/format/language, hit Transcribe.

### CLI

```bash
python cli.py <source> [options]
```

**Examples:**

```bash
# YouTube / social media URL
python cli.py https://www.youtube.com/watch?v=xxx

# Local file
python cli.py video.mp4

# Local file → SRT subtitles, medium model
python cli.py video.mp4 -m medium -f srt

# Batch: entire folder (recursive)
python cli.py C:\Videos\

# Multiple files, custom output dir
python cli.py vid1.mp4 vid2.mp4 -o C:\Output\

# Force language (faster + more accurate)
python cli.py video.mp4 -l en
```

**Options:**

| Flag | Default | Choices |
|------|---------|---------|
| `-m / --model` | `base` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `-f / --format` | `txt` | `txt`, `srt` |
| `-l / --language` | auto-detect | `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `zh`, `ja`, `ar`, `lv` … |
| `-o / --output` | same dir as input | path to output directory |

## Model Guide

| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| tiny | fastest | lowest | ~1 GB |
| base | fast | decent | ~1 GB |
| small | moderate | good | ~2 GB |
| medium | slow | very good | ~5 GB |
| large-v3 | slowest | best | ~10 GB |

First run downloads model weights automatically and caches them.

## Stack

- [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — local Whisper transcription
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — URL audio download
- [`FastAPI`](https://fastapi.tiangolo.com/) + `uvicorn` — web UI backend
- [`Click`](https://click.palletsprojects.com/) — CLI
- `ffmpeg` — audio extraction

## Project Structure

```
transcriber/
  core.py        # routing, audio extraction, Whisper inference
  downloader.py  # yt-dlp wrapper
  formatter.py   # txt and SRT output
web/
  app.py         # FastAPI server
  static/
    index.html   # single-page UI
cli.py           # CLI entry point
```
