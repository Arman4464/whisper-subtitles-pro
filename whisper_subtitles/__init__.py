"""
Whisper Subtitles Pro
=====================
Universal 100% Accurate Audio-to-Subtitles & Alignment Engine.
Supports Faster-Whisper, Wav2Vec2/CTC Forced Alignment, and Gemini Audio API.
Zero Desync, Word-Level Timestamps, and Autonomous GitHub Actions Cloud Runner.
"""

__version__ = "1.0.0"
__author__ = "Arman4464"
__license__ = "MIT"

from .formatter import SubtitleFormatter
from .aligner import ForcedAligner
from .transcriber import UniversalTranscriber
from .cloud_runner import GitHubCloudRunner

__all__ = [
    "SubtitleFormatter",
    "ForcedAligner",
    "UniversalTranscriber",
    "GitHubCloudRunner",
    "__version__",
]
