from linnaeus_test.database import Database
from linnaeus_test.llm_base import LLMBase
from linnaeus_test.manager import Manager
from linnaeus_test.ab_test_page import get_ab_test_page

from typing import Any


class Interface:
    def __init__(
        self,
        llm_api_cfgs: dict[str, dict[str, Any]],
        model_presets: list[dict[str, Any]],
        use_case: str | None = None,
        eval_question: str | None = None,
    ):
        self.model_presets: list[LLMBase] = [
            self.merged_model_cfg(llm_api_cfgs, model_preset)
            for model_preset in model_presets
        ]
        self.use_case = use_case
        self.eval_question = eval_question

    @staticmethod
    def merged_model_cfg(
        llm_api_cfgs: dict[str, dict[str, Any]], model_preset: dict[str, Any]
    ) -> LLMBase:
        model = model_preset["model"]
        if model not in llm_api_cfgs:
            raise ValueError(f"Model {model} not found in LLM API configuration.")
        llm_api_cfg = llm_api_cfgs[model]
        params = llm_api_cfg.get("defaults", {})
        for k, v in model_preset.items():
            if k not in ("model", "system_message"):
                params[k] = v
        return LLMBase.create(
            api=llm_api_cfg["api"],
            model=model,
            api_url=llm_api_cfg["url"],
            api_key=llm_api_cfg["key"],
            system_message=model_preset.get("system_message"),
            model_params=params,
        )

    def launch(self, database_filename: str, **kwargs) -> None:
        database = Database(database_filename)
        manager = Manager(self.model_presets, database)
        get_ab_test_page(manager, self.use_case, self.eval_question).launch(**kwargs)
