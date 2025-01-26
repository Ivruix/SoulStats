from ml_backend.agents.prompts import EMOTION_ANALYZER_PROMPT
from ml_backend.data_types.chat import Chat
from ml_backend.data_types.emotion import Emotion


class EmotionAnalyzer:
    def __init__(self, model):
        self.model = model

    def analyze(self, chat):
        chat_str = chat.as_string()
        new_chat = Chat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(EMOTION_ANALYZER_PROMPT))[0].text
        return Emotion.from_russian_name(result.lower().strip())
