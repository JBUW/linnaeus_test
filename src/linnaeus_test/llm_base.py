import abc
import dataclasses
import glob
import importlib
import os
import typing


@dataclasses.dataclass
class LLMBase(abc.ABC):
    name_to_api_class: typing.ClassVar[dict[str, "LLMBase"]] = {}

    api_url: str
    api_key: str
    model: str
    system_message: str | None = None
    model_params: dict[str, type] = dataclasses.field(default_factory=dict)

    def __init_subclass__(cls):
        if cls.api_identifier in cls.name_to_api_class:
            raise ValueError(
                f'Multiple API classes with identifier "{cls.api_identifier}": '
                f"{cls.name_to_api_class[cls.api_identifier].__name__}, {cls.__name__}"
            )
        cls.name_to_api_class[cls.api_identifier] = cls

    @classmethod
    def create(cls, api: str, **kwargs) -> typing.Self:
        if api not in cls.name_to_api_class:
            raise ValueError(f"Unrecognized API identifier: {api}")
        api_class = cls.name_to_api_class[api]
        return api_class(**kwargs)

    @abc.abstractmethod
    def call(self, user_message: str) -> str:
        pass

    @staticmethod
    def to_message_list(messages: dict[str, str]) -> list[dict[str, str]]:
        return [
            {"role": role, "content": content} for role, content in messages.items()
        ]


# Automatically import all subclasses.
if len(LLMBase.name_to_api_class) == 0:
    subclass_dir = "llms"
    subclass_pattern = os.path.join(os.path.dirname(__file__), subclass_dir, "*.py")
    for filename in glob.glob(subclass_pattern):
        basename = os.path.basename(filename)
        if basename == "__init__.py":
            continue
        submodule = os.path.splitext(basename)[0]
        importlib.import_module(f"{__package__}.{subclass_dir}.{submodule}")
