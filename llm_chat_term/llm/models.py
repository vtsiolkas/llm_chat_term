from pydantic import BaseModel


class ModelConfig(BaseModel):
    provider: str
    name: str
    temperature: float | None = None


def get_models():
    return [
        ModelConfig(provider="google", name="gemini-2.5-pro"),
        ModelConfig(provider="deepseek", name="deepseek-reasoner"),
        ModelConfig(provider="openai", name="gtp-5-mini"),
        ModelConfig(provider="openai", name="gpt-5"),
        ModelConfig(
            provider="anthropic",
            name="claude-sonnet-4-5-20250929",
        ),
    ]
