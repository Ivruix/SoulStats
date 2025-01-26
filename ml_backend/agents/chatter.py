from random import choice
from ml_backend.agents.prompts import MESSAGE_WRITER_PROMPT, WILL_END_SOON_PROMPT, CLOSING_MESSAGE_PROMPT


def generate_first_message():
    first_messages = [
        "Привет! Что сегодня было интересного?",
        "Привет! Как прошел твой день?",
        "Привет! Есть что-то, чем хочешь поделиться?"
    ]
    return choice(first_messages)


class Chatter:
    def __init__(self, model):
        self.model = model

    def generate_response(self, chat, messages_left):
        if len(chat.messages) == 0:
            return generate_first_message()

        if messages_left == 1:
            system_prompt = CLOSING_MESSAGE_PROMPT
        else:
            system_prompt = MESSAGE_WRITER_PROMPT
            if messages_left <= 2:
                system_prompt = system_prompt + " " + WILL_END_SOON_PROMPT

        result = self.model.run(chat.with_system_prompt(system_prompt, "Привет"))[0].text

        return result
