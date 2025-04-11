from yandex_cloud_ml_sdk._models.completions.result import AlternativeStatus

from ml_backend.agents.prompts import MESSAGE_WRITER_PROMPT, CLOSING_MESSAGE_PROMPT, FACTS_PROMTS
from ml_backend.agents.yandex_sdk import get_sdk
from ml_backend.data_types.agent_chat import AgentChat


class Chatter:
    def __init__(self, temperature=0.5):
        sdk = get_sdk()
        chatter_model = sdk.models.completions("yandexgpt")
        chatter_model = chatter_model.configure(temperature=temperature)
        self.model = chatter_model

    def generate_response(self, chat, facts, last_message):
        # last_message - True, если это последний вопрос в чате
        if last_message:
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

        # Искусственное начало диалога
        before_chat = AgentChat()
        before_chat.add_user_message("Привет.")
        before_chat.add_assistant_message("Привет! Как прошел ваш день?")

        print(before_chat.with_chat(chat).with_system_prompt(system_prompt).as_list())
        result = self.model.run(before_chat.with_chat(chat).with_system_prompt(system_prompt).as_list())[0]

        if result.status == AlternativeStatus.CONTENT_FILTER:
            return "Давайте завершим этот диалог."

        return result.text
