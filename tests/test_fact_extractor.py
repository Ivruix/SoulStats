import unittest
from ml_backend.agents.fact_extractor import FactExtractor
from ml_backend.data_types.agent_chat import AgentChat
from unittest.mock import Mock


class TestFactExtractor(unittest.TestCase):
    def setUp(self):
        self.fact_extractor = FactExtractor()
        self.fact_extractor.model = Mock()
        self.model = self.fact_extractor.model

    def test_extract_facts(self):
        chat = AgentChat()
        chat.add_user_message("Я работаю программистом.")
        self.model.run.return_value = [Mock(text="{\"facts\":[\"Пользователь работает программистом.\"]}")]

        facts = self.fact_extractor.extract_facts(chat)

        self.assertEqual(facts, ["Пользователь работает программистом."])


if __name__ == '__main__':
    unittest.main()
