from llm_chat_term.llm.tools.definitions import GetWeather
from llm_chat_term.llm.tools.main import register_model


@register_model
def handle_weather(model: GetWeather):
    return f"The weather in {model.location} is rainy with storms."
