from ml_backend.agents.prompts import CHAT_EXTENDER_PROMPT
from ml_backend.data_types.agent_chat import AgentChat


class ChatExtender:
    def __init__(self, model):
        self.model = model

    def should_extend(self, chat):
        chat_str = chat.as_string()
        new_chat = AgentChat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(CHAT_EXTENDER_PROMPT).as_list())[0].text
        return result.lower().strip() != "нет"
