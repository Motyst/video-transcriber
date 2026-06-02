def format_txt(segments) -> str:
    return '\n'.join(seg.text.strip() for seg in segments if seg.text.strip())


def format_srt(segments) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.extend([
            str(i),
            f"{_srt_time(seg.start)} --> {_srt_time(seg.end)}",
            seg.text.strip(),
            "",
        ])
    return '\n'.join(lines)


def _srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
