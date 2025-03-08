"""Configuration module for the terminal LLM chatbot."""

import sys

import yaml
from pydantic import BaseModel, Field, SecretStr

from llm_chat_term.db import get_config_file


def get_default_models():
    return [
        ModelConfig(
            provider="anthropic",
            model="claude-3-7-sonnet-20250219",
            api_key=SecretStr(""),
        ),
        ModelConfig(provider="openai", model="gpt-4o", api_key=SecretStr("")),
        ModelConfig(provider="openai", model="o3-mini", api_key=SecretStr("")),
    ]


class ModelConfig(BaseModel):
    provider: str
    model: str
    api_key: SecretStr = Field(default=SecretStr(""))
    temperature: float | None = None


class LLMConfig(BaseModel):
    models: list[ModelConfig] = Field(default_factory=get_default_models)
    system_prompt: str = (
        "You are a helpful assistant responding to a user's questions in a PC terminal application.\n"
        "The user is an experienced software engineer, your answers should be concise and not repetitive.\n"
        "Skip conclusions and summarizations of your answers.\n"
        "If the user asks for a change in code, don't return the whole code, just the changed segment(s).\n"
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


def load_config() -> AppConfig:
    """Load configuration from YAML file with fallbacks to default values."""
    config_file = get_config_file()

    # Start with default configuration
    config = AppConfig()

    # Load configuration from file if it exists
    if not config_file.exists():
        try:
            # Dump the default config model to a dictionary
            default_config = config.model_dump()

            # Make sure API keys are empty strings, not SecretStr objects
            for model in default_config["llm"]["models"]:
                model["api_key"] = ""

            with config_file.open("w") as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            sys.stdout.write(f"Created default configuration file at {config_file}\n")
            sys.stdout.write(
                "Add your models/API key(s) there and start `llm_chat_term` again\n",
            )
            sys.exit(0)
        except Exception as e:
            error_msg = f"Error creating default config file: {e}\n"
            sys.stderr.write(error_msg)
            sys.exit(1)
    else:
        try:
            with config_file.open() as f:
                user_config = yaml.safe_load(f)

            if user_config:
                # Update with user configuration
                config = AppConfig.model_validate(user_config)
        except Exception as e:
            error_msg = f"Error loading config file: {e!s}\n"
            sys.stderr.write(error_msg)
            sys.exit(1)

    return config


config: AppConfig = load_config()
