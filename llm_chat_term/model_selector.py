from llm_chat_term.config import ModelConfig, config
from llm_chat_term.prompt_menu import Menu


def select_model() -> ModelConfig:
    models = config.llm.models

    menu = Menu(
        [model.model for model in models],
        " Select a chat (j/k to move, Enter to select, e to edit, d to delete, q to quit):\n",
    )

    result = menu.run()

    return models[result]
