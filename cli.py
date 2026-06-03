#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

import click

from transcriber.core import SUPPORTED_EXTENSIONS, is_url, transcribe

PROJECT_ROOT = Path(__file__).parent
DEFAULT_URL_DIR = PROJECT_ROOT / 'transcriptions' / 'url'
DEFAULT_LOCAL_DIR = PROJECT_ROOT / 'transcriptions' / 'local'


def _safe_filename(title: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    safe = safe.strip().replace(' ', '_')
    return safe[:80] or 'transcription'


def _build_url_header(meta: dict, url: str) -> str:
    lines = []
    if meta.get('title'):
        lines.append(f"Title: {meta['title']}")
    if meta.get('platform'):
        lines.append(f"Platform: {meta['platform']}")
    lines.append(f"URL: {url}")
    return '\n'.join(lines) + '\n\n'


@click.command()
@click.argument('source', nargs=-1, required=True)
@click.option('--model', '-m', default='base',
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large-v3']),
              show_default=True, help='Whisper model size')
@click.option('--format', '-f', 'output_format', default='txt',
              type=click.Choice(['txt', 'srt']), show_default=True, help='Output format')
@click.option('--language', '-l', default=None, help='Language code (e.g. en, es). Auto-detect if omitted.')
@click.option('--output', '-o', default=None, help='Output directory (overrides default transcriptions/ layout)')
def main(source, model, output_format, language, output):
    """Transcribe video/audio from URLs or local files/folders.

    SOURCE can be one or more: URLs, file paths, or folder paths.
    Folders are scanned recursively for supported media files.
    """
    sources = []
    for s in source:
        if is_url(s):
            sources.append(s)
        else:
            p = Path(s)
            if p.is_dir():
                found = sorted(f for f in p.rglob('*') if f.suffix.lower() in SUPPORTED_EXTENSIONS)
                if not found:
                    click.echo(f"Warning: no supported files in {s}", err=True)
                sources.extend(str(f) for f in found)
            elif p.is_file():
                sources.append(str(p))
            else:
                click.echo(f"Error: {s} not found", err=True)
                sys.exit(1)

    if not sources:
        click.echo("No valid sources found.", err=True)
        sys.exit(1)

    for src in sources:
        label = src if len(src) <= 70 else '...' + src[-67:]
        click.echo(f"\nProcessing: {label}")

        last_msg = ['']
        captured_meta = [{}]

        def progress(msg: str, pct=None):
            if pct is not None:
                filled = pct // 5
                bar = '█' * filled + '░' * (20 - filled)
                line = f"  [{bar}] {pct:3d}%  {msg}"
            else:
                line = f"  {msg}"
            click.echo(line + ' ' * 10, nl=False)
            click.echo('\r', nl=False)
            last_msg[0] = msg

        def on_metadata(meta: dict):
            captured_meta[0] = meta

        try:
            result = transcribe(
                src,
                model_size=model,
                output_format=output_format,
                language=language,
                progress_callback=progress,
                metadata_callback=on_metadata,
            )
            click.echo()

            if is_url(src):
                out_dir = output or str(DEFAULT_URL_DIR)
                meta = captured_meta[0]
                stem = _safe_filename(meta.get('title', '')) if meta.get('title') else 'transcription'
                out_name = f"{stem}.{output_format}"
                header = _build_url_header(meta, src)
                content = header + result
            else:
                out_dir = output or str(DEFAULT_LOCAL_DIR)
                out_name = f"{Path(src).stem}.{output_format}"
                content = result

            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, out_name)

            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)

            click.echo(f"  Saved: {out_path}")

        except Exception as e:
            click.echo(f"\n  Error: {e}", err=True)


if __name__ == '__main__':
    main()
