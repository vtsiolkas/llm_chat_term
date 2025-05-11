from pydantic import BaseModel


class ModelConfig(BaseModel):
    provider: str
    name: str
    temperature: float | None = None


def get_models():
    return [
        ModelConfig(provider="google", name="gemini-2.5-pro-exp-03-25"),
        ModelConfig(provider="deepseek", name="deepseek-chat"),
        ModelConfig(provider="openai", name="o3-mini"),
        ModelConfig(provider="openai", name="gpt-4o"),
        ModelConfig(
            provider="anthropic",
            name="claude-3-7-sonnet-20250219",
        ),
    ]
