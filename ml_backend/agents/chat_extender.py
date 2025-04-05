from yandex_cloud_ml_sdk._models.completions.result import AlternativeStatus

from ml_backend.agents.prompts import CHAT_EXTENDER_PROMPT
from ml_backend.data_types.agent_chat import AgentChat
from ml_backend.agents.yandex_sdk import get_sdk


class ChatExtender:
    def __init__(self, temperature=0.0):
        sdk = get_sdk()
        chat_extender_model = sdk.models.completions("yandexgpt")
        chat_extender_model = chat_extender_model.configure(temperature=temperature)
        self.model = chat_extender_model

    def should_extend(self, chat):
        chat_str = chat.as_string()
        new_chat = AgentChat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(CHAT_EXTENDER_PROMPT).as_list())[0]
        if result.status == AlternativeStatus.CONTENT_FILTER:
            return False

        return result.text.lower().strip() != "нет"
