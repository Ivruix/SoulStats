from ml_backend.agents.prompts import MESSAGE_WRITER_PROMPT, WILL_END_SOON_PROMPT, CLOSING_MESSAGE_PROMPT
from ml_backend.data_types.chat import Chat

class Chatter:
    def __init__(self, model):
        self.model = model

    def generate_response(self, chat, messages_left):
        # messages_left - сколько сообщений ассистенту осталось написать
        if messages_left == 1:
            system_prompt = CLOSING_MESSAGE_PROMPT
        else:
            system_prompt = MESSAGE_WRITER_PROMPT
            if messages_left <= 2:
                system_prompt = system_prompt + " " + WILL_END_SOON_PROMPT

        before_chat = Chat()
        before_chat.add_user_message("Привет.")
        before_chat.add_assistant_message("Привет! Как прошел ваш день?")

        result = self.model.run(before_chat.with_chat(chat).with_system_prompt(system_prompt).as_list())[0].text

        return result
