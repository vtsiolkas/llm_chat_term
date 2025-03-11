"""Configuration module for the terminal LLM chatbot."""

import sys

import yaml
from pydantic import BaseModel, Field, SecretStr

from llm_chat_term.db import get_config_file


class ModelConfig(BaseModel):
    provider: str
    name: str
    temperature: float | None = None


def get_default_models():
    return [
        ModelConfig(
            provider="anthropic",
            name="claude-3-7-sonnet-20250219",
        ),
        ModelConfig(provider="openai", name="gpt-4o"),
        ModelConfig(provider="openai", name="o3-mini"),
    ]


class ApiKey(BaseModel):
    provider: str
    api_key: SecretStr = Field(default=SecretStr(""))


def get_default_api_keys() -> list[ApiKey]:
    return [ApiKey(provider="anthropic"), ApiKey(provider="openai")]


class LLMConfig(BaseModel):
    models: list[ModelConfig] = Field(default_factory=get_default_models)
    api_keys: list[ApiKey] = Field(default_factory=get_default_api_keys)
    system_prompt: str = (
        "You are a helpful assistant responding to a user's questions in a PC terminal application.\n"
        "The user is an experienced software engineer, your answers should be concise and not repetitive.\n"
        "Skip conclusions and summarizations of your answers.\n"
        "If the user asks for a change in code, don't return the whole code, just the changed segment(s).\n"
        "Return your answers in markdown format, and wrap code in ``` blocks, but avoid using headings."
    )


class UIConfig(BaseModel):
    prompt_symbol: str = ">>> "
    user: str = "user"
    assistant: str = "assistant"


class ColorConfig(BaseModel):
    user: str = "cyan"
    assistant: str = "grey39"
    system: str = "yellow"


class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    colors: ColorConfig = Field(default_factory=ColorConfig)
    audio_device: str = ""


def save_config(conf: AppConfig) -> None:
    """Save the config model to the YAML file."""
    config_file = get_config_file()
    conf_dict = conf.model_dump()

    for api_key in conf_dict["llm"]["api_keys"]:
        api_key["api_key"] = api_key["api_key"].get_secret_value()

    with config_file.open("w") as f:
        yaml.dump(conf_dict, f, default_flow_style=False, sort_keys=False)


def load_config() -> AppConfig:
    """Load configuration from YAML file with fallbacks to default values."""
    config_file = get_config_file()

    # Start with default configuration
    config = AppConfig()

    # Load configuration from file if it exists
    if not config_file.exists():
        try:
            save_config(config)
            sys.stdout.write(f"Created default configuration file at {config_file}\n")
        except Exception as e:
            error_msg = f"Error creating default config file: {e}\n"
            sys.stderr.write(error_msg)
            sys.exit(1)
    else:
        try:
            with config_file.open() as f:
                user_config = yaml.safe_load(f)

            return AppConfig.model_validate(user_config)
        except Exception as e:
            error_msg = f"Error loading config file: {e!s}\n"
            sys.stderr.write(error_msg)
            sys.exit(1)

    return config


config: AppConfig = load_config()
