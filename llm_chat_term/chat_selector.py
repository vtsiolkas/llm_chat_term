import sys

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.console import Console

from llm_chat_term import db, utils


def select_chat() -> str | None:
    """Display a simple in-terminal menu for selecting a chat.

    Returns:
        Selected chat ID or None if user cancels
    """
    # Get all chats
    all_chats: list[str] = db.list_all_chats()
    if len(all_chats) == 0:
        return create_new_chat()

    chats = ["Create new chat"] + all_chats
    selected_index = 0
    result = None

    # Create key bindings
    kb = KeyBindings()

    @kb.add("j")
    @kb.add("down")
    def _(event: KeyPressEvent):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(chats)
        event.app.invalidate()

    @kb.add("k")
    @kb.add("up")
    def _(event: KeyPressEvent):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(chats)
        event.app.invalidate()

    @kb.add("enter")
    def _(event: KeyPressEvent):
        nonlocal result
        result = selected_index
        event.app.exit()

    @kb.add("e")
    def _(event: KeyPressEvent):
        chat_id = chats[selected_index]
        utils.open_in_editor(chat_id)
        event.app.invalidate()

    @kb.add("d")
    def _(event: KeyPressEvent):
        nonlocal selected_index
        if selected_index == 0:
            event.app.invalidate()
            return
        chat_id = chats[selected_index]
        utils.delete_chat(chat_id)
        chats.pop(selected_index)
        selected_index -= 1
        event.app.invalidate()

    @kb.add("q")
    @kb.add("c-c")
    def _(event: KeyPressEvent):
        event.app.exit()
        sys.exit(1)

    def get_menu_text() -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        result.append(
            (
                "class:title",
                (
                    " Select a chat (j/k to move, Enter to select, "
                    "e to edit, d to delete, q to quit):\n"
                ),
            )
        )

        for i, chat in enumerate(chats):
            if i == selected_index:
                result.append(("green", f" > {chat}\n"))
            else:
                result.append(("", f"   {chat}\n"))

        return result

    # Create the layout
    layout = Layout(HSplit([Window(FormattedTextControl(get_menu_text))]))

    # Create and run the application
    app = Application(  # pyright: ignore[reportUnknownVariableType]
        layout=layout,
        key_bindings=kb,
        full_screen=False,
        mouse_support=True,
    )
    app.run()

    # Handle the result
    if result is None:
        return None

    if result == 0:  # Create new chat
        return create_new_chat()
    else:
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


def main():
    # For testing
    selected = select_chat()
    if selected:
        print(f"Selected chat: {selected}")
    else:
        print("No chat selected")
