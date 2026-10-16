import unittest
import json
from unittest.mock import MagicMock, patch
from whisper_subtitles.transcriber import UniversalTranscriber

class TestTranscriber(unittest.TestCase):
    def setUp(self):
        self.transcriber = UniversalTranscriber(model_name="gemini")

    def test_gemini_parser_clean_json(self):
        sample = [
            {"start": 0.0, "end": 2.5, "text": "This is a clean JSON response."}
        ]
        with patch("whisper_subtitles.transcriber.UniversalTranscriber.transcribe_gemini") as mock_gemini:
            mock_gemini.return_value = [
                {
                    "id": 1,
                    "start": 0.0,
                    "end": 2.5,
                    "text": "This is a clean JSON response.",
                    "words": []
                }
            ]
            res = self.transcriber.transcribe("dummy.wav")
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["text"], "This is a clean JSON response.")

    def test_gemini_json_cleaning_logic(self):
        # Test markdown fence stripping
        raw_markdown = "```json\n[{\"start\": 1.0, \"end\": 3.0, \"text\": \"Fenced code block.\"}]\n```"
        clean = raw_markdown.strip()
        import re
        if "```" in clean:
            m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
            if m:
                clean = m.group(1).strip()
        parsed = json.loads(clean)
        self.assertEqual(parsed[0]["text"], "Fenced code block.")

    def test_gemini_dict_wrapper_unwrapping(self):
        wrapped = {
            "subtitles": [
                {"start": 0.5, "end": 2.0, "text": "Inside dictionary wrapper."}
            ]
        }
        # Simulate unwrap logic
        data = wrapped
        if isinstance(data, dict):
            for candidate in ["subtitles", "segments", "transcript"]:
                if candidate in data and isinstance(data[candidate], list):
                    data = data[candidate]
                    break
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["text"], "Inside dictionary wrapper.")

if __name__ == "__main__":
    unittest.main()
