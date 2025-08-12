from ..llm_base import LLMBase

import time
from typing import Final


class Dummy(LLMBase):
    api_identifier: Final[str] = "dummy"

    def call(self, user_message: str) -> str:
        params = self.__dict__
        model_params = params.get("model_params", {})
        if "sleep" in model_params:
            time.sleep(model_params["sleep"])
        return "Output from " + str(
            {k: v for k, v in params.items() if v is not None}
        )
