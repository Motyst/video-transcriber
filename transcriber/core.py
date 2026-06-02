import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional

from faster_whisper import WhisperModel

from .downloader import download_audio
from .formatter import format_srt, format_txt

SUPPORTED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.opus'}

_model_cache: dict = {}


def is_url(source: str) -> bool:
    return source.startswith(('http://', 'https://'))


def _get_model(model_size: str) -> WhisperModel:
    if model_size not in _model_cache:
        _model_cache[model_size] = WhisperModel(model_size, device='auto', compute_type='auto')
    return _model_cache[model_size]


def _extract_audio(video_path: str, output_dir: str) -> str:
    audio_path = os.path.join(output_dir, 'audio.wav')
    subprocess.run(
        ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
         '-ar', '16000', '-ac', '1', audio_path, '-y'],
        check=True, capture_output=True,
    )
    return audio_path


def transcribe(
    source: str,
    model_size: str = 'base',
    output_format: str = 'txt',
    language: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
    metadata_callback: Optional[Callable[[dict], None]] = None,
) -> str:
    def progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    model = _get_model(model_size)

    with tempfile.TemporaryDirectory() as tmp:
        if is_url(source):
            progress('downloading audio')
            audio_path, meta = download_audio(source, tmp)
            if metadata_callback and meta:
                metadata_callback(meta)
        else:
            ext = Path(source).suffix.lower()
            if ext in {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus'}:
                audio_path = source
            else:
                progress('extracting audio')
                audio_path = _extract_audio(source, tmp)

        progress('transcribing')
        segments, _info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        segments = list(segments)

        progress('done')

        if output_format == 'srt':
            return format_srt(segments)
        return format_txt(segments)
