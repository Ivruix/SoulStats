from ml_backend.data_types.agent_chat import AgentChat
from ml_backend.agents.prompts import FACT_EXTRACTOR_PROMPT


class FactExtractor:
    def __init__(self, model):
        self.model = model

    def extract_facts(self, chat):
        chat_str = chat.as_string()
        new_chat = AgentChat()
        new_chat.add_user_message(chat_str)

        result = self.model.run(new_chat.with_system_prompt(FACT_EXTRACTOR_PROMPT).as_list())[0].text
        result = [line.strip() for line in result.splitlines() if line.strip() != ""]

        return result
