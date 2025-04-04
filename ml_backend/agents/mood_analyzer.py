from yandex_cloud_ml_sdk._models.completions.result import AlternativeStatus

from ml_backend.agents.prompts import MOOD_ANALYZER_PROMPT
from ml_backend.agents.yandex_sdk import get_sdk
from ml_backend.data_types.agent_chat import AgentChat


class MoodAnalyzer:
    def __init__(self, temperature=0.0):
        sdk = get_sdk()
        mood_analyzer_model = sdk.models.completions("yandexgpt")
        mood_analyzer_model = mood_analyzer_model.configure(temperature=temperature)
        self.model = mood_analyzer_model

    def analyze(self, chat):
        chat_str = chat.as_string()
        new_chat = AgentChat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(MOOD_ANALYZER_PROMPT).as_list())[0]

        if result.status == AlternativeStatus.CONTENT_FILTER:
            return None

        try:
            result = int(result.text) + 3
            if result > 5 or result < 1:
                return None
            return result
        except:
            return None
