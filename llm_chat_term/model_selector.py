import sys

from rich.console import Console

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


def create_new_chat() -> str | None:
    """Prompt the user to create a new chat."""
    from prompt_toolkit import prompt

    console = Console()
    console.print("[green]Create a New Chat[/green]")

    try:
        chat_id = prompt("Enter a name for your new chat(blank for anonymous chat): ")
    except KeyboardInterrupt:
        console.print("\nExiting...")
        sys.exit(0)

    if not chat_id.strip():
        return None

    console.print(f"[blue]Created new chat: {chat_id}[/blue]")

    return chat_id
