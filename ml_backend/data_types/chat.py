class Chat:
    def __init__(self):
        self.messages = []

    @staticmethod
    def from_db_messages(messages):
        chat = Chat()
        for content, by_user in messages:
            if by_user:
                chat.add_user_message(content)
            else:
                chat.add_assistant_message(content)
        return chat

    def add_user_message(self, message):
        self.messages.append(
            {
                "role": "user",
                "text": message
            }
        )

    def add_assistant_message(self, message):
        self.messages.append(
            {
                "role": "assistant",
                "text": message
            }
        )

    def with_system_prompt(self, system_prompt, user_message=None):
        prompt_dict = {
            "role": "system",
            "text": system_prompt
        }

        if user_message is None:
            return [prompt_dict] + self.messages

        user_message_dict = {
            "role": "user",
            "text": user_message
        }

        return [prompt_dict, user_message_dict] + self.messages

    def as_string(self):
        mapping = {
            "system": "Система",
            "user": "Пользователь",
            "assistant": "Ассистент"
        }
        return "\n".join(f"{mapping[message['role']]}: {message['text']}" for message in self.messages)

    def __len__(self):
        return len(self.messages)
