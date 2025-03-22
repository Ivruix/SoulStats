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
        chat.add_user_message("Как прошел ваш день?")
        self.model.run.return_value = [Mock(text="Мой день прошел хорошо.")]

        response = self.chatter.generate_response(chat, [], 3)

        self.assertEqual(response, "Мой день прошел хорошо.")


if __name__ == '__main__':
    unittest.main()
