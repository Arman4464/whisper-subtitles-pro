import unittest
from whisper_subtitles.formatter import SubtitleFormatter

class TestSubtitleFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = SubtitleFormatter(max_cpl=42, max_lines=2)
        self.sample_segments = [
            {
                "id": 1,
                "start": 0.0,
                "end": 2.5,
                "text": "Hello world, this is a subtitle test.",
                "words": [
                    {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.99},
                    {"word": "world,", "start": 0.5, "end": 1.0, "probability": 0.98},
                    {"word": "this", "start": 1.0, "end": 1.5, "probability": 0.99},
                    {"word": "is", "start": 1.5, "end": 1.8, "probability": 0.99},
                    {"word": "a", "start": 1.8, "end": 2.0, "probability": 0.99},
                    {"word": "subtitle", "start": 2.0, "end": 2.3, "probability": 0.97},
                    {"word": "test.", "start": 2.3, "end": 2.5, "probability": 0.99},
                ]
            }
        ]

    def test_srt_format(self):
        srt = self.formatter.to_srt(self.sample_segments)
        self.assertIn("1\n00:00:00,000 --> 00:00:02,500", srt)
        self.assertIn("Hello world, this is a subtitle test.", srt)

    def test_vtt_format(self):
        vtt = self.formatter.to_vtt(self.sample_segments)
        self.assertTrue(vtt.startswith("WEBVTT"))
        self.assertIn("00:00:00.000 --> 00:00:02.500", vtt)

    def test_json_format(self):
        res = self.formatter.to_json(self.sample_segments)
        self.assertIn("Universal Alignment Engine", res)
        self.assertIn("\"total_cues\": 1", res)

if __name__ == "__main__":
    unittest.main()
