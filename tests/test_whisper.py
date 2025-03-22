import unittest
from ml_backend.speech_recognition.whisper_singleton import WhisperRecognizer
from unittest.mock import patch, Mock


class TestWhisperRecognizer(unittest.TestCase):
    @patch('ml_backend.speech_recognition.whisper_singleton.whisper.load_model')
    def setUp(self, mock_load_model):
        self.recognizer = WhisperRecognizer()
        self.recognizer.model = Mock()

    def test_transcribe(self):
        self.recognizer.model.transcribe.return_value = {"text": "Привет, мир!"}

        result = self.recognizer.transcribe("path/to/audio/file")

        self.assertEqual(result, "Привет, мир!")


if __name__ == '__main__':
    unittest.main()
