from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent


def confirm_prompt(message: str) -> bool:
    """
    Display a yes/no prompt that immediately returns on y/n keypress.
    Returns True for 'y' and False for 'n'.
    """
    bindings = KeyBindings()
    result = False

    @bindings.add("y")
    @bindings.add("Y")
    def _(event: KeyPressEvent):
        nonlocal result
        result = True
        event.app.exit()

    @bindings.add("n")
    @bindings.add("N")
    def _(event: KeyPressEvent):
        nonlocal result
        result = False
        event.app.exit()

    try:
        prompt(
            message + " (y/n) ",
            key_bindings=bindings,
            default="",
        )
    except KeyboardInterrupt:
        return False

    return result
