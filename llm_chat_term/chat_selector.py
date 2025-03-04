import sys

from prompt_toolkit.key_binding import KeyPressEvent
from rich.console import Console

from llm_chat_term import db, utils
from llm_chat_term.prompt_menu import Menu


def handle_delete(event: KeyPressEvent, menu: Menu):
    if menu.selected_index == 0:
        return
    utils.delete_chat(menu.items[menu.selected_index])
    menu.items.pop(menu.selected_index)
    setattr(menu, "selected_index", menu.selected_index - 1)
    event.app.invalidate()


def handle_edit(event: KeyPressEvent, menu: Menu):
    utils.open_in_editor(menu.items[menu.selected_index])
    event.app.invalidate()


def select_chat() -> str | None:
    all_chats = db.list_all_chats()
    if len(all_chats) == 0:
        return create_new_chat()

    chats = ["Create new chat"] + all_chats

    menu = Menu(
        chats,
        " Select a chat (j/k to move, Enter to select, e to edit, d to delete, q to quit):\n",
    )

    menu.add_binding("e", handle_edit)

    menu.add_binding("d", handle_delete)

    result = menu.run()

    if result is None:
        return None
    if result == 0:
        return create_new_chat()

    return chats[result]


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
