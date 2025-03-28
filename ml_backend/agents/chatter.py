from ml_backend.agents.prompts import MESSAGE_WRITER_PROMPT, WILL_END_SOON_PROMPT, CLOSING_MESSAGE_PROMPT, FACTS_PROMTS
from ml_backend.data_types.agent_chat import AgentChat


class Chatter:
    def __init__(self, model):
        self.model = model

    def generate_response(self, chat, facts, messages_left):
        # messages_left - сколько сообщений ассистенту осталось написать
        if messages_left == 1:
            system_prompt = CLOSING_MESSAGE_PROMPT
        else:
            # Промпт для ассистента
            system_prompt = MESSAGE_WRITER_PROMPT

            # Если есть факты, добавляем их в промпт
            if facts:
                system_prompt += "\n"
                system_prompt += FACTS_PROMTS
                for fact in facts:
                    system_prompt += f"- {fact}\n"

            # Если осталось мало сообщений, добавляем предупреждение
            if messages_left <= 2:
                system_prompt += "\n"
                system_prompt += WILL_END_SOON_PROMPT

        # Искусственное начало диалога
        before_chat = AgentChat()
        before_chat.add_user_message("Привет.")
        before_chat.add_assistant_message("Привет! Как прошел ваш день?")

        print(before_chat.with_chat(chat).with_system_prompt(system_prompt).as_list())

        result = self.model.run(before_chat.with_chat(chat).with_system_prompt(system_prompt).as_list())[0].text

        return result
