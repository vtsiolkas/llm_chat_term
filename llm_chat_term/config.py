"""Configuration module for the terminal LLM chatbot."""

import sys
import yaml

from pydantic import BaseModel, Field, SecretStr
from llm_chat_term.db import get_config_file


class LLMConfig(BaseModel):
    provider: str = "anthropic"
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    anthropic_key: SecretStr = Field(default=SecretStr(""))
    model: str = "claude-3-7-sonnet-20250219"
    temperature: float = 0.4
    system_prompt: str = (
        "You are a helpful assistant responding to a user's questions in a terminal environment. "
        "The user is an experienced software engineer, your answers should be concise and not "
        "repetitive. Skip conclusions and summarizations of your answers."
        "If the user asks for a change in code, don't return the whole code, just the changed segment(s)."
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
            default_config["llm"]["openai_api_key"] = ""
            default_config["llm"]["anthropic_key"] = ""

            with open(config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            print(f"Created default configuration file at {config_file}")
            print("Add your API key(s) there and start `term-chat` again")
            sys.exit(0)
        except Exception as e:
            print(f"Error creating default config file: {e}")
    else:
        try:
            with open(config_file, "r") as f:
                user_config = yaml.safe_load(f)

            if user_config:
                # Update with user configuration
                config = AppConfig.model_validate(user_config)
        except Exception as e:
            print(f"Error loading config file: {e}")

    return config


config = load_config()
