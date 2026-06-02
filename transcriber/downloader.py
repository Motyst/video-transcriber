import os
import yt_dlp


def download_audio(url: str, output_dir: str) -> tuple:
    """Download audio from URL via yt-dlp. Returns (audio_path, metadata_dict)."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '0',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    metadata = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            metadata['title'] = info.get('title', '')
            metadata['platform'] = info.get('extractor_key', info.get('extractor', ''))

    audio_path = os.path.join(output_dir, 'audio.wav')
    if os.path.exists(audio_path):
        return audio_path, metadata

    for f in os.listdir(output_dir):
        if f.startswith('audio.'):
            return os.path.join(output_dir, f), metadata

    raise FileNotFoundError("Audio download failed — check URL or yt-dlp support for this platform")
