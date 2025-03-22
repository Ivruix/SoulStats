class AgentChat:
    def __init__(self, messages=None):
        if messages is None:
            self.messages = []
        else:
            self.messages = messages

    @staticmethod
    def from_db_messages(messages):
        chat = AgentChat()
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

    def with_chat(self, other):
        return AgentChat(self.messages + other.messages)

    def with_system_prompt(self, system_prompt, user_message=None):
        prompt_dict = {
            "role": "system",
            "text": system_prompt
        }

        return AgentChat([prompt_dict] + self.messages)

    def as_list(self):
        return self.messages

    def as_string(self):
        mapping = {
            "system": "Система",
            "user": "Пользователь",
            "assistant": "Ассистент"
        }
        return "\n".join(f"{mapping[message['role']]}: {message['text']}" for message in self.messages)

    def assistant_message_count(self):
        count = 0
        for message in self.messages:
            if message["role"] == "assistant":
                count += 1
        return count

    def __len__(self):
        return len(self.messages)
