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
            },
            {
                "id": 2,
                "start": 3661.123,
                "end": 3665.456,
                "text": "Over one hour later, subtitle timing remains completely accurate.",
                "words": []
            }
        ]

    def test_srt_format(self):
        srt = self.formatter.to_srt(self.sample_segments)
        self.assertIn("1\n00:00:00,000 --> 00:00:02,500", srt)
        self.assertIn("Hello world, this is a subtitle test.", srt)
        # Verify 1-hour rollover
        self.assertIn("2\n01:01:01,123 --> 01:01:05,456", srt)

    def test_vtt_format(self):
        vtt = self.formatter.to_vtt(self.sample_segments)
        self.assertTrue(vtt.startswith("WEBVTT"))
        self.assertIn("00:00:00.000 --> 00:00:02.500", vtt)
        self.assertIn("01:01:01.123 --> 01:01:05.456", vtt)

    def test_json_format(self):
        res = self.formatter.to_json(self.sample_segments)
        self.assertIn("Universal Alignment Engine", res)
        self.assertIn("\"total_cues\": 2", res)
        self.assertIn("\"confidence\": 0.99", res)

    def test_lrc_format(self):
        lrc = self.formatter.to_lrc(self.sample_segments)
        self.assertIn("[00:00.00]Hello world, this is a subtitle test.", lrc)

    def test_txt_format(self):
        txt_timed = self.formatter.to_txt(self.sample_segments, include_timestamps=True)
        self.assertIn("[00:00] Hello world", txt_timed)
        txt_plain = self.formatter.to_txt(self.sample_segments, include_timestamps=False)
        self.assertNotIn("[00:00]", txt_plain)
        self.assertIn("Hello world", txt_plain)

    def test_timestamp_edge_cases(self):
        # Negative timestamp protection
        self.assertEqual(SubtitleFormatter.format_timestamp(-5.0, "srt"), "00:00:00,000")
        self.assertEqual(SubtitleFormatter.format_timestamp(0.0, "srt"), "00:00:00,000")
        self.assertEqual(SubtitleFormatter.format_timestamp(59.999, "srt"), "00:00:59,999")
        self.assertEqual(SubtitleFormatter.format_timestamp(60.000, "srt"), "00:01:00,000")

    def test_text_wrapping(self):
        # 1. Text that fits within 2 lines (< 84 chars) should be balanced into exactly 2 lines
        two_line_text = "Spoken dialogue that needs to be cleanly split into two balanced lines."
        wrapped_two = self.formatter.wrap_text(two_line_text)
        lines_two = wrapped_two.split("\n")
        self.assertEqual(len(lines_two), 2)
        for line in lines_two:
            self.assertLessEqual(len(line), self.formatter.max_cpl)

        # 2. Text that exceeds 2 lines must strictly respect max_cpl on every single line
        long_text = "This is a very long line of spoken dialogue that needs to be properly wrapped according to broadcast limits."
        wrapped_long = self.formatter.wrap_text(long_text)
        lines_long = wrapped_long.split("\n")
        for line in lines_long:
            self.assertLessEqual(len(line), self.formatter.max_cpl)

if __name__ == "__main__":
    unittest.main()
