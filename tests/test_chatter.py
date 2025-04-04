import unittest
from ml_backend.agents.chatter import Chatter
from ml_backend.data_types.agent_chat import AgentChat
from unittest.mock import Mock


class TestChatter(unittest.TestCase):
    def setUp(self):
        self.model = Mock()
        self.chatter = Chatter(self.model)

    def test_generate_response(self):
        chat = AgentChat()
        chat.add_user_message("Мой день прошел хорошо.")
        self.model.run.return_value = [Mock(text="Что именно вам понравилось?")]

        response = self.chatter.generate_response(chat, [], False)

        self.assertEqual(response, "Что именно вам понравилось?")


if __name__ == '__main__':
    unittest.main()
