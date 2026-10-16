import os
import wave
import struct
import math
import tempfile
import unittest
from whisper_subtitles.aligner import ForcedAligner

class TestForcedAligner(unittest.TestCase):
    def setUp(self):
        self.aligner = ForcedAligner()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_synthetic_wav(self, filename: str, channels: int = 1, sample_rate: int = 16000) -> str:
        """
        Creates a synthetic WAV with 2 active tone bursts separated by 0.5s of absolute silence.
        Burst 1: 0.0s to 1.0s (Speech 1)
        Silence: 1.0s to 1.5s (Pause)
        Burst 2: 1.5s to 2.5s (Speech 2)
        Total: 2.5 seconds
        """
        path = os.path.join(self.temp_dir.name, filename)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            # Generate 2.5s
            total_samples = int(2.5 * sample_rate)
            data = []
            for i in range(total_samples):
                t = i / float(sample_rate)
                # Burst 1: 0.1s to 0.9s
                # Silence: 0.9s to 1.4s
                # Burst 2: 1.4s to 2.3s
                if (0.1 <= t <= 0.9) or (1.4 <= t <= 2.3):
                    val = int(8000 * math.sin(2 * math.pi * 440 * t))
                else:
                    val = 0

                for _ in range(channels):
                    data.append(val)

            raw = struct.pack(f"<{len(data)}h", *data)
            wf.writeframes(raw)

        return path

    def test_read_audio_mono(self):
        wav_path = self._create_synthetic_wav("mono.wav", channels=1)
        pcm, sr, ch, dur = ForcedAligner.read_audio_pcm(wav_path)
        self.assertEqual(ch, 1)
        self.assertAlmostEqual(dur, 2.5, places=2)
        self.assertEqual(len(pcm), int(2.5 * sr * 2))

    def test_read_audio_stereo_downmix(self):
        wav_path = self._create_synthetic_wav("stereo.wav", channels=2)
        pcm, sr, ch, dur = ForcedAligner.read_audio_pcm(wav_path)
        # Stereo should be downmixed to mono
        self.assertEqual(ch, 1)
        self.assertAlmostEqual(dur, 2.5, places=2)
        # Length in bytes must equal 2.5s of 16-bit mono
        self.assertEqual(len(pcm), int(2.5 * sr * 2))

    def test_sentence_segmentation(self):
        text = "This is sentence one. Here is sentence two! And sentence three? Finally, sentence four."
        sentences = ForcedAligner.segment_text_into_sentences(text)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(sentences[0], "This is sentence one.")
        self.assertEqual(sentences[1], "Here is sentence two!")

    def test_speech_pauses_detection(self):
        wav_path = self._create_synthetic_wav("speech_pauses.wav", channels=1)
        pcm, sr, ch, dur = ForcedAligner.read_audio_pcm(wav_path)
        energies = ForcedAligner.compute_frame_energy(pcm, frame_size=int(sr * 0.02))
        pauses = ForcedAligner.find_speech_pauses(energies, frame_sec=0.02, min_silence_sec=0.20)
        
        # Verify that a pause was found around 0.9s - 1.4s
        self.assertTrue(len(pauses) >= 1)
        pause_mid = pauses[0]["midpoint"]
        self.assertTrue(0.85 <= pause_mid <= 1.45, f"Pause midpoint {pause_mid} not in expected window")

    def test_forced_alignment_sync(self):
        wav_path = self._create_synthetic_wav("align_sync.wav", channels=1)
        transcript = "Welcome to the test audio. We are verifying precision alignment."
        segments = self.aligner.align(wav_path, transcript)

        self.assertEqual(len(segments), 2)
        # Segment 1 should start near 0.1 and end around the pause (0.9 - 1.4s)
        seg1 = segments[0]
        seg2 = segments[1]

        self.assertLessEqual(seg1["start"], 0.2)
        self.assertTrue(0.8 <= seg1["end"] <= 1.5)
        self.assertEqual(seg1["end"], seg2["start"], "Adjacent segment boundaries must match exactly with zero gap")
        self.assertTrue(seg2["end"] <= 2.5)

        # Word-level timestamp sanity
        all_words = seg1["words"] + seg2["words"]
        for i in range(len(all_words) - 1):
            self.assertLessEqual(all_words[i]["start"], all_words[i]["end"])
            self.assertLessEqual(all_words[i]["end"], all_words[i + 1]["start"] + 0.001)

if __name__ == "__main__":
    unittest.main()
