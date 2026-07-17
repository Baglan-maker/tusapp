"""Server-side audio inspection.

The client caps recordings at 120s, but the client is not a trust boundary:
10 MB of m4a is ~20 minutes, and STT is billed per minute. We read the real
duration from the container (pure-Python, no ffmpeg) and reject anything longer.
"""

import io

from mutagen import MutagenError
from mutagen.mp4 import MP4


class InvalidAudioError(ValueError):
    """The bytes are not a readable audio container."""


def duration_seconds(data: bytes) -> float:
    """Duration of an m4a/MP4 recording, in seconds."""
    try:
        audio = MP4(io.BytesIO(data))  # type: ignore[no-untyped-call]  # mutagen ships no stubs
    except (MutagenError, OSError, ValueError) as exc:
        raise InvalidAudioError("unreadable audio") from exc
    length = getattr(audio.info, "length", None)
    if not isinstance(length, (int, float)) or length <= 0:
        raise InvalidAudioError("audio has no duration")
    return float(length)
