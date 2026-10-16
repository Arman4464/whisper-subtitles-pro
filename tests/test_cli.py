import os
import sys
import wave
import struct
import tempfile
import unittest
from unittest.mock import patch
import whisper_subtitles.cli as cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_wav(self, name: str) -> str:
        p = os.path.join(self.temp_dir.name, name)
        with wave.open(p, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            data = [int(4000 * (i % 2)) for i in range(16000)]
            wf.writeframes(struct.pack(f"<{len(data)}h", *data))
        return p

    def test_cli_info_command(self):
        wav_path = self._create_wav("test_info.wav")
        test_args = ["wsub", "info", wav_path]
        with patch.object(sys, "argv", test_args):
            # Should run without raising any exceptions
            try:
                cli.main()
            except SystemExit as e:
                self.assertEqual(e.code, 0)

    def test_cli_align_command_positional(self):
        wav_path = self._create_wav("test_align.wav")
        txt_path = os.path.join(self.temp_dir.name, "text.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Line one. Line two.")

        out_dir = os.path.join(self.temp_dir.name, "out")
        test_args = ["wsub", "align", wav_path, txt_path, "--output-dir", out_dir, "--format", "srt,vtt,json"]
        with patch.object(sys, "argv", test_args):
            try:
                cli.main()
            except SystemExit as e:
                self.assertEqual(e.code, 0)

        # Check outputs exist
        self.assertTrue(os.path.exists(os.path.join(out_dir, "test_align_aligned.srt")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "test_align_aligned.vtt")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "test_align_aligned.json")))

    def test_cli_align_command_flag(self):
        wav_path = self._create_wav("test_align_flag.wav")
        txt_path = os.path.join(self.temp_dir.name, "text_flag.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Testing flag alignment.")

        out_dir = os.path.join(self.temp_dir.name, "out_flag")
        test_args = ["wsub", "align", wav_path, "--transcript", txt_path, "--output-dir", out_dir, "--format", "all"]
        with patch.object(sys, "argv", test_args):
            try:
                cli.main()
            except SystemExit as e:
                self.assertEqual(e.code, 0)

        self.assertTrue(os.path.exists(os.path.join(out_dir, "test_align_flag_aligned.srt")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "test_align_flag_aligned.lrc")))

if __name__ == "__main__":
    unittest.main()
