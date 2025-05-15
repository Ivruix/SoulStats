import unittest
from unittest.mock import Mock
from ml_backend.agents.chat_extender import ChatExtender
from ml_backend.data_types.agent_chat import AgentChat
from yandex_cloud_ml_sdk._models.completions.result import AlternativeStatus


class TestChatExtender(unittest.TestCase):
    def setUp(self):
        self.chat_extender = ChatExtender()
        self.chat_extender.model = Mock()
        self.model = self.chat_extender.model

    def test_should_extend_returns_false_on_content_filter(self):
        chat = AgentChat()
        chat.add_user_message("Привет!")
        self.model.run.return_value = [Mock(status=AlternativeStatus.CONTENT_FILTER)]

        result = self.chat_extender.should_extend(chat)

        self.assertFalse(result)

    def test_should_extend_returns_false_on_negative_response(self):
        chat = AgentChat()
        chat.add_user_message("Привет!")
        self.model.run.return_value = [Mock(status=None, text="нет")]

        result = self.chat_extender.should_extend(chat)

        self.assertFalse(result)

    def test_should_extend_returns_true_on_positive_response(self):
        chat = AgentChat()
        chat.add_user_message("Привет!")
        self.model.run.return_value = [Mock(status=None, text="да")]

        result = self.chat_extender.should_extend(chat)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
