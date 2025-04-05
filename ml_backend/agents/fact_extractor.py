from yandex_cloud_ml_sdk._models.completions.result import AlternativeStatus

from ml_backend.agents.yandex_sdk import get_sdk
from ml_backend.data_types.agent_chat import AgentChat
from ml_backend.agents.prompts import FACT_EXTRACTOR_PROMPT

import json


class FactExtractor:
    def __init__(self, temperature=0.0):
        sdk = get_sdk()
        fact_extractor_model = sdk.models.completions("yandexgpt")
        fact_extractor_model = fact_extractor_model.configure(temperature=temperature)
        self.model = fact_extractor_model

    def extract_facts(self, chat):
        chat_str = chat.as_string()
        new_chat = AgentChat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(FACT_EXTRACTOR_PROMPT).as_list())[0]

        if result.status == AlternativeStatus.CONTENT_FILTER:
            return []

        result = result.text
        result = result[result.find("{"):result.rfind("}") + 1]
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            return []
        result = result.get("facts", [])

        return result
