from llm_chat_term.llm.models import ModelConfig, get_models
from llm_chat_term.ui.prompt_menu import Menu


def select_model() -> ModelConfig:
    models = get_models()

    menu = Menu(
        [model.name for model in models],
        " Select a model (j/k to move, Enter to select, e to edit, d to delete, q to quit):\n",
    )

    result = menu.run()

    return models[result]
