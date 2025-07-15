from linnaeus_test.database import Database
from linnaeus_test.llm_base import LLM_Base

import dataclasses

@dataclasses.dataclass
class Manager:
    model_presets: LLM_Base
    database: Database

    def __post_init__(self):
        self.session_to_model_ids = {}

    def get_model_texts(self, user_session, text):
        model_ids = self.get_model_ids(user_session)
        return [self.model_presets[model_id].call(text) for model_id in model_ids]

    def get_model_ids(self, user_session):
        if user_session in self.session_to_model_ids:
            *model_ids, processed_feedback = self.session_to_model_ids[user_session]
            if processed_feedback:
                self.session_to_model_ids[user_session] = [
                    (model_ids[0] + 2) % len(self.model_presets),
                    (model_ids[1] + 2) % len(self.model_presets),
                    False,
                ]
        else:
            self.session_to_model_ids[user_session] = [0, 1, False]
        return self.session_to_model_ids[user_session]

    def process_feedback(self, user_session, eval, feedback):
        if user_session not in self.session_to_model_ids:
            return
        *models, processed_feedback = self.session_to_model_ids[user_session]
        if eval in (0, 1):
            print(
                f"{'Updated' if processed_feedback else 'New'}: {models[eval]} is better."
            )
        self.session_to_model_ids[user_session][2] = True
        self.database.add_evaluation(user_session, models[0], models[1], eval, feedback)
