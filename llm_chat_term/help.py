from rich.console import Console

from llm_chat_term.config import config

# fmt: off
COMMANDS: dict[str, list[str]] = {
    ":help": [
        "Displays this help message."
    ],
    ":info": [
        "Displays info about this chat."
    ],
    ":edit :e": [
        "Opens the conversation history in $EDITOR (vim by default).",
        "Edit it and save and it will be reloaded in the message history."
    ],
    ":chat": [
        "Display the menu to select a different chat."
    ],
    ":model": [
        "Display the menu to select a different chat."
    ],
    ":redraw": [
        "Redraw the whole conversation."
    ],
    ":think {prompt}": [
        "Enable thinking mode only for this question (Claude only)."
    ],
    ":read {path}": [
        "Embed a text file in the prompt (replaces the line with :read)."
    ],
    ":exit": [
        "Exits the application. The conversation is saved if not anonymous chat."
    ],
}
# fmt: on


def print_help(console: Console):
    console.print("Available commands", style=f"bold {config.colors.system}")
    console.print()
    max_length: int = max(*[len(cmd) for cmd in COMMANDS.keys()])
    padding = 4
    for cmd, info_list in COMMANDS.items():
        console.print(cmd, style=config.colors.system, end="")
        d_length = max_length + padding - len(cmd)
        console.print(" " * d_length, end="")
        for idx, info in enumerate(info_list):
            if idx == 0:
                console.print(f"{info}", style=config.colors.system)
            else:
                console.print(
                    f"{' ' * (max_length + padding)}{info}", style=config.colors.system
                )
    console.print()
