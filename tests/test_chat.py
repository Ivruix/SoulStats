import unittest
from ml_backend.data_types.agent_chat import AgentChat


class TestChat(unittest.TestCase):
    def setUp(self):
        self.chat = AgentChat()

    def test_add_user_message(self):
        self.chat.add_user_message("Привет!")
        self.assertEqual(len(self.chat), 1)
        self.assertEqual(self.chat.messages[0]["role"], "user")
        self.assertEqual(self.chat.messages[0]["text"], "Привет!")

    def test_add_assistant_message(self):
        self.chat.add_assistant_message("Здравствуйте!")
        self.assertEqual(len(self.chat), 1)
        self.assertEqual(self.chat.messages[0]["role"], "assistant")
        self.assertEqual(self.chat.messages[0]["text"], "Здравствуйте!")

    def test_with_chat(self):
        other_chat = AgentChat()
        other_chat.add_user_message("Как дела?")
        combined_chat = self.chat.with_chat(other_chat)
        self.assertEqual(len(combined_chat), 1)
        self.assertEqual(combined_chat.messages[0]["text"], "Как дела?")

    def test_with_system_prompt(self):
        system_prompt = "Это системное сообщение."
        new_chat = self.chat.with_system_prompt(system_prompt)
        self.assertEqual(len(new_chat), 1)
        self.assertEqual(new_chat.messages[0]["role"], "system")
        self.assertEqual(new_chat.messages[0]["text"], system_prompt)

    def test_as_list(self):
        self.chat.add_user_message("Привет!")
        self.chat.add_assistant_message("Здравствуйте!")
        messages_list = self.chat.as_list()
        self.assertEqual(len(messages_list), 2)
        self.assertEqual(messages_list[0]["role"], "user")
        self.assertEqual(messages_list[1]["role"], "assistant")

    def test_as_string(self):
        self.chat.add_user_message("Привет!")
        self.chat.add_assistant_message("Здравствуйте!")
        chat_str = self.chat.as_string()
        self.assertIn("Пользователь: Привет!", chat_str)
        self.assertIn("Ассистент: Здравствуйте!", chat_str)

    def test_assistant_message_count(self):
        self.chat.add_user_message("Привет!")
        self.chat.add_assistant_message("Здравствуйте!")
        self.assertEqual(self.chat.assistant_message_count(), 1)


if __name__ == '__main__':
    unittest.main()
