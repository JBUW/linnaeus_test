from linnaeus_test.database import Database
from linnaeus_test.llm_base import LLMBase

import concurrent.futures
import dataclasses
import random


@dataclasses.dataclass
class Manager:
    model_presets: list[LLMBase]
    database: Database

    def __post_init__(self):
        self.session_to_model_presets = {}
        self.rng = random.Random()

    def get_model_texts(self, user_session, text: str) -> tuple[str, str]:
        user_model_presets = [
            model_preset for model_preset in self.rng.sample(self.model_presets, 2)
        ]
        self.session_to_model_presets[user_session] = user_model_presets

        # Make model calls in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return list(
                executor.map(lambda preset: preset.call(text), user_model_presets)
            )

    def process_evaluation(self, user_session, **eval_data):
        if user_session not in self.session_to_model_presets:
            raise ValueError(f"User session not found.")
        self.database.add_evaluation(
            user_session=user_session,
            model_presets=self.session_to_model_presets[user_session],
            **eval_data,
        )
        del self.session_to_model_presets[user_session]
