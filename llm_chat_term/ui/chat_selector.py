import sys

from prompt_toolkit.key_binding import KeyPressEvent
from rich.console import Console

from llm_chat_term import db, utils
from llm_chat_term.ui.prompt_menu import Menu


def handle_delete(event: KeyPressEvent, menu: Menu):
    if menu.selected_index == 0:
        return
    utils.delete_chat(menu.items[menu.selected_index])
    menu.items.pop(menu.selected_index)
    menu.selected_index = menu.selected_index - 1
    event.app.invalidate()


def handle_edit(event: KeyPressEvent, menu: Menu):
    utils.open_in_editor(menu.items[menu.selected_index])
    event.app.invalidate()


def select_chat() -> str:
    all_chats = db.list_all_chats()
    if len(all_chats) == 0:
        return create_new_chat()

    chats = ["Create new chat", *all_chats]

    menu = Menu(
        chats,
        " Select a chat (j/k to move, Enter to select, e to edit, d to delete, q to quit):\n",
    )

    menu.add_binding("e", handle_edit)

    menu.add_binding("d", handle_delete)

    result = menu.run()

    if result == 0:
        return create_new_chat()

    return chats[result]


def create_new_chat(*, allow_blank: bool = True) -> str:
    """Prompt the user to create a new chat."""
    from prompt_toolkit import prompt

    console = Console()
    if allow_blank:
        console.print("[green]Create a New Chat...[/green]")
    else:
        console.print("[green]Pick a name to save the chat before editing...[/green]")
    prompt_text = "Enter a name"
    prompt_text += "(blank for anonymous chat): " if allow_blank else ": "

    while True:
        try:
            chat_id = prompt(prompt_text)
        except KeyboardInterrupt:
            if allow_blank:
                console.print("\nExiting...")
                sys.exit(0)
            else:
                chat_id = ""
                console.print("Cannot edit conversation without a chat name...")

        chat_id = chat_id.strip()

        if chat_id:
            file_path = db.get_chat_file(chat_id)
            if file_path.exists():
                console.print(
                    (
                        f"[red]Chat [bold]{chat_id}[/bold] "
                        f"already exists at: [bold]{file_path}[/bold][/red]"
                    )
                )
                continue
            console.print(
                f"[blue]Chat conversation will be persisted to: {file_path}[/blue]"
            )

        return chat_id
