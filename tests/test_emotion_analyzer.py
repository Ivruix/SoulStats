import unittest
from ml_backend.agents.emotion_analyzer import EmotionAnalyzer
from ml_backend.data_types.agent_chat import AgentChat
from ml_backend.data_types.emotion import Emotion
from unittest.mock import Mock


class TestEmotionAnalyzer(unittest.TestCase):
    def setUp(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.emotion_analyzer.model = Mock()
        self.model = self.emotion_analyzer.model

    def test_extract_emotion(self):
        chat = AgentChat()
        chat.add_user_message("Я очень рад.")
        self.model.run.return_value = [Mock(text="радость")]

        emotion = self.emotion_analyzer.extract_emotion(chat)
        
        self.assertEqual(emotion, Emotion.joy)


if __name__ == '__main__':
    unittest.main()
