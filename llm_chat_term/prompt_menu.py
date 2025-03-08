import sys
from collections.abc import Callable

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import FormattedTextControl, HSplit, Layout, Window


class Menu:
    def __init__(self, items: list[str], title: str):
        self.items = items
        self.title = title
        self.selected_index = 0
        self.result = 0
        self.kb = KeyBindings()
        self._setup_default_bindings()

    def _setup_default_bindings(self):
        @self.kb.add("j")
        @self.kb.add("down")
        def _(event: KeyPressEvent):
            self.selected_index = (self.selected_index + 1) % len(self.items)
            event.app.invalidate()

        @self.kb.add("k")
        @self.kb.add("up")
        def _(event: KeyPressEvent):
            self.selected_index = (self.selected_index - 1) % len(self.items)
            event.app.invalidate()

        @self.kb.add("enter")
        def _(event: KeyPressEvent):
            self.result = self.selected_index
            event.app.exit()

        @self.kb.add("q")
        @self.kb.add("c-c")
        def _(event: KeyPressEvent):
            event.app.exit()
            sys.exit(1)

    def add_binding(self, key: str, handler: Callable[[KeyPressEvent, "Menu"], None]):
        # Wrapper to add custom bindings
        @self.kb.add(key)
        def _(event: KeyPressEvent):
            handler(event, self)

    def run(self) -> int:
        # Create the layout
        layout = Layout(HSplit([Window(FormattedTextControl(self._get_menu_text))]))

        # Create and run the application
        app = Application(  # pyright: ignore[reportUnknownVariableType]
            layout=layout,
            key_bindings=self.kb,
            full_screen=False,
            mouse_support=True,
        )
        app.run()

        return self.result

    def _get_menu_text(self) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        result.append(
            (
                "class:title",
                self.title,
            )
        )

        for i, item in enumerate(self.items):
            if i == self.selected_index:
                result.append(("green", f" > {item}\n"))
            else:
                result.append(("", f"   {item}\n"))

        return result
