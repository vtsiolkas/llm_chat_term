from pydantic import BaseModel


class ModelConfig(BaseModel):
    provider: str
    name: str
    temperature: float | None = None


def get_models():
    return [
        ModelConfig(
            provider="anthropic",
            name="claude-3-7-sonnet-20250219",
        ),
        ModelConfig(provider="openai", name="gpt-4o"),
        ModelConfig(provider="openai", name="o3-mini"),
        ModelConfig(provider="deepseek", name="deepseek-chat"),
    ]
