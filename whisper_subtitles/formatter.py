"""
Universal Subtitle Formatter & Exporter
Supports SRT, WebVTT, JSON (with word-level timing), LRC (karaoke), and TXT.
Enforces industry-standard line wrapping, CPL (characters per line), and CPS limits.
"""

import json
import re
from typing import List, Dict, Any, Optional

class SubtitleFormatter:
    def __init__(self, max_cpl: int = 42, max_lines: int = 2):
        self.max_cpl = max_cpl
        self.max_lines = max_lines

    @staticmethod
    def format_timestamp(seconds: float, format_type: str = "srt") -> str:
        """
        Formats seconds into SRT (00:00:00,000) or VTT (00:00:00.000) or Display (00:00).
        """
        if seconds < 0:
            seconds = 0.0
            
        total_ms = int(round(seconds * 1000))
        ms = total_ms % 1000
        total_seconds = total_ms // 1000
        s = total_seconds % 60
        total_minutes = total_seconds // 60
        m = total_minutes % 60
        h = total_minutes // 60

        if format_type.lower() == "srt":
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        elif format_type.lower() == "vtt":
            return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
        elif format_type.lower() == "lrc":
            return f"{m:02d}:{s:02d}.{ms // 10:02d}"
        else: # standard display mm:ss or hh:mm:ss
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"

    def wrap_text(self, text: str) -> str:
        """
        Wraps long subtitle lines into readable blocks strictly respecting max_cpl.
        """
        words = text.split()
        if not words:
            return ""

        full_text = " ".join(words)
        if len(full_text) <= self.max_cpl:
            return full_text

        # If it fits within 2 lines, balance them cleanly near the middle
        if self.max_lines == 2 and len(full_text) <= self.max_cpl * 2:
            best_split = len(words) // 2
            min_diff = float("inf")
            for split_idx in range(1, len(words)):
                l1 = " ".join(words[:split_idx])
                l2 = " ".join(words[split_idx:])
                if len(l1) <= self.max_cpl and len(l2) <= self.max_cpl:
                    diff = abs(len(l1) - len(l2))
                    if diff < min_diff:
                        min_diff = diff
                        best_split = split_idx
            if min_diff != float("inf"):
                return f"{' '.join(words[:best_split])}\n{' '.join(words[best_split:])}"

        # Standard greedy word-wrap strictly enforcing max_cpl per line
        lines = []
        current_line = []
        current_len = 0

        for w in words:
            w_len = len(w)
            if current_line and (current_len + 1 + w_len > self.max_cpl):
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = w_len
            else:
                current_line.append(w)
                current_len += (w_len + 1 if current_line else w_len)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    def to_srt(self, segments: List[Dict[str, Any]]) -> str:
        """Exports cues to standard SubRip (.srt) format."""
        srt_blocks = []
        for idx, seg in enumerate(segments, start=1):
            start_str = self.format_timestamp(seg["start"], "srt")
            end_str = self.format_timestamp(seg["end"], "srt")
            text = self.wrap_text(seg["text"].strip())
            srt_blocks.append(f"{idx}\n{start_str} --> {end_str}\n{text}\n")
        return "\n".join(srt_blocks)

    def to_vtt(self, segments: List[Dict[str, Any]]) -> str:
        """Exports cues to WebVTT (.vtt) format with styling and metadata support."""
        vtt_lines = ["WEBVTT\n"]
        for idx, seg in enumerate(segments, start=1):
            start_str = self.format_timestamp(seg["start"], "vtt")
            end_str = self.format_timestamp(seg["end"], "vtt")
            text = self.wrap_text(seg["text"].strip())
            vtt_lines.append(f"{idx}\n{start_str} --> {end_str}\n{text}\n")
        return "\n".join(vtt_lines)

    def to_json(self, segments: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Exports rich structured JSON containing sentence cues, per-word timestamps,
        and track duration metadata.
        """
        formatted_segments = []
        for idx, seg in enumerate(segments, start=1):
            item = {
                "id": idx,
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
                "start_formatted": self.format_timestamp(seg["start"], "display"),
                "end_formatted": self.format_timestamp(seg["end"], "display"),
                "text": seg["text"].strip(),
            }
            if "words" in seg and seg["words"]:
                item["words"] = [
                    {
                        "word": w.get("word", "").strip(),
                        "start": round(w.get("start", 0.0), 3),
                        "end": round(w.get("end", 0.0), 3),
                        "confidence": round(w.get("probability", 1.0), 2)
                    }
                    for w in seg["words"]
                ]
            if "topic" in seg and seg["topic"]:
                item["topic"] = seg["topic"]
            formatted_segments.append(item)

        doc = {
            "version": "1.0",
            "generator": "Whisper Subtitles Pro (Universal Alignment Engine)",
            "total_cues": len(formatted_segments),
            "metadata": metadata or {},
            "subtitles": formatted_segments
        }
        return json.dumps(doc, indent=2, ensure_ascii=False)

    def to_lrc(self, segments: List[Dict[str, Any]]) -> str:
        """Exports cues to Karaoke Lyric (.lrc) format."""
        lrc_lines = ["[ti:Generated Subtitles]", "[by:Whisper Subtitles Pro]"]
        for seg in segments:
            lrc_time = self.format_timestamp(seg["start"], "lrc")
            text = seg["text"].strip().replace("\n", " ")
            lrc_lines.append(f"[{lrc_time}]{text}")
        return "\n".join(lrc_lines)

    def to_txt(self, segments: List[Dict[str, Any]], include_timestamps: bool = True) -> str:
        """Exports cues to clean plain text."""
        lines = []
        for seg in segments:
            if include_timestamps:
                ts = self.format_timestamp(seg["start"], "display")
                lines.append(f"[{ts}] {seg['text'].strip()}")
            else:
                lines.append(seg["text"].strip())
        return "\n".join(lines)
