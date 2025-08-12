from ..llm_base import LLMBase

import dataclasses
import requests
from typing import Final


@dataclasses.dataclass
class OpenAIHttpLLM(LLMBase):
    api_identifier: Final[str] = "openai"
    api_version: str = "2025-04-01-preview"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def call(self, user_message: str) -> str:
        data = {
            "messages": self.to_message_list(
                {"system": self.system_message, "user": user_message}
            ),
        } | self.model_params

        response = requests.post(
            f"{self.api_url}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}",
            headers=self.headers,
            json=data,
        )
        response_json = response.json()
        if "error" in response_json:
            raise ValueError(response.json()["error"]["message"])
        return next(iter(response_json["choices"]))["message"]["content"]
