import unittest
from ml_backend.agents.mood_analyzer import MoodAnalyzer
from ml_backend.data_types.agent_chat import AgentChat
from unittest.mock import Mock


class TestMoodAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mood_analyzer = MoodAnalyzer()
        self.mood_analyzer.model = Mock()
        self.model = self.mood_analyzer.model

    def test_analyze(self):
        chat = AgentChat()
        chat.add_user_message("Сегодня был хороший день.")
        self.model.run.return_value = [Mock(text="2")]

        mood = self.mood_analyzer.analyze(chat)

        self.assertEqual(mood, 5)


if __name__ == '__main__':
    unittest.main()
