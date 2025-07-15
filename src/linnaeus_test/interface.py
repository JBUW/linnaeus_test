from linnaeus_test.database import Database
from linnaeus_test.llm_base import LLM_Base
from linnaeus_test.manager import Manager
from linnaeus_test.gradio_app import get_summarized_page
from typing import Any


class Interface:
    def __init__(self, llm_api_cfgs: dict[str, dict[str, Any]], model_presets: dict):
        self.model_presets = [
            self.merged_model_cfg(llm_api_cfgs, model_preset)
            for model_preset in model_presets
        ]

    @staticmethod
    def merged_model_cfg(llm_api_cfgs, model_preset):
        model = model_preset["model"]
        if model not in llm_api_cfgs:
            raise ValueError(f"Model {model} not found in LLM API configuration.")
        llm_api_cfg = llm_api_cfgs[model]
        params = llm_api_cfg.get("defaults", {})
        for k, v in model_preset.items():
            if k not in ("model", "system-message"):
                params[k] = v
        return LLM_Base.create(
            api=llm_api_cfg["api"],
            model=model,
            api_url=llm_api_cfg["url"],
            api_key=llm_api_cfg["key"],
            system_message=model_preset.get("system-message"),
            model_params=params,
        )

    def get_test_subjects(self):
        return [
            {
                "id": i,
                "model": model_preset.model,
                "parameters": model_preset.model_params,
                "system-message": model_preset.system_message,
            }
            for i, model_preset in enumerate(self.model_presets)
        ]

    def launch(self, database_filename: str, share=False) -> None:
        database = Database(database_filename)
        # a.export_to_csv('test.csv')
        # exit(0)
        manager = Manager(self.model_presets, database)
        get_summarized_page(manager).launch(share=share)
        '''
        for model_preset in self.model_presets:
            content = model_preset.call("I am going to Paris, what should I see?")
            print(content)
            print(model_preset.model)
        '''