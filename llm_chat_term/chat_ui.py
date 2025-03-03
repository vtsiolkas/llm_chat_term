"""Terminal UI for the LLM chatbot using prompt_toolkit and rich."""

from typing import cast, override

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.rule import Rule
from rich.syntax import Syntax
from rich.text import Text

from llm_chat_term.config import config


class CodeBlockNoPadding(CodeBlock):
    """A code block with syntax highlighting."""

    @override
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(
            code, self.lexer_name, theme=self.theme, word_wrap=True, padding=0
        )
        yield syntax


class ChatUI:
    """Terminal UI for the chatbot."""

    def __init__(self):
        self.console = Console()

        # Set up the prompt style
        self.style = Style.from_dict(
            {
                "prompt": f"fg:{config.colors.user}",
            }
        )

        # Create a session for the prompt
        self.session = PromptSession[str](
            style=self.style,
            history=InMemoryHistory(),
            multiline=True,
            vi_mode=False,
            prompt_continuation=lambda width, line_number, is_soft_wrap: " "
            * len(config.ui.prompt_symbol),
        )

        # Track whether we're currently streaming a response
        self.streaming = False
        # Track whether we're in a thinking block
        self.thinking = False
        self.current_response = ""
        self.live = Live()

    def _get_ai_title(self):
        content = Text(
            f" {config.ui.assistant} ", style=f"bold white on {config.colors.assistant}"
        )
        return Rule(content, style=f"on {config.colors.assistant}", characters=" ")

    def _get_user_title(self):
        content = Text(
            f" {config.ui.user} ", style=f"bold black on {config.colors.user}"
        )
        return Rule(content, style=f"on {config.colors.user}", characters=" ")

    def _get_markdown(self, content: str):
        try:
            text = Markdown(content)
            text.elements["fence"] = CodeBlockNoPadding
            text.elements["code_block"] = CodeBlockNoPadding
        except Exception:
            text = Text(content)

        return text

    def display_welcome_message(self):
        """Display a welcome message when a chat starts."""
        self.console.print(
            "Type your messages and press Alt(Esc)+Enter to send. Use Enter for newlines.",
            style=config.colors.system,
        )
        self.console.print(
            "Type '/help' for commands help, '/exit' or Ctrl+D to exit.",
            style=config.colors.system,
        )
        self.console.print()

    def display_help(self):
        self.console.print("Available commands", style=f"bold {config.colors.system}")
        self.console.print()
        self.console.print(
            "/help: Displays this help message.", style=config.colors.system
        )
        self.console.print(
            "/info: Displays info about this chat.", style=config.colors.system
        )
        self.console.print(
            "/edit, /e: Opens the conversation history in $EDITOR (vim by default).",
            style=config.colors.system,
        )
        self.console.print(
            "           Edit it and save and it will be reloaded in the message history.",
            style=config.colors.system,
        )
        self.console.print(
            "/select: Display the menu to select a different chat",
            style=config.colors.system,
        )
        self.console.print(
            "/redraw: Redraw the whole conversation",
            style=config.colors.system,
        )
        self.console.print(
            "/think {prompt}: Enable thinking mode only for this question (Claude only)",
            style=config.colors.system,
        )
        self.console.print(
            "/exit: Exits the application. The conversation is saved if not anonymous chat.",
            style=config.colors.system,
        )
        self.console.print()

    def display_info(self, chat_id: str | None):
        if chat_id:
            self.console.print(
                f"Selected chat: {chat_id}", style=f"bold {config.colors.system}"
            )
        else:
            self.console.print("Anonymous chat", style=f"bold {config.colors.system}")

    def get_user_input(self) -> str:
        """Get multiline input from the user."""
        try:
            self.console.print(self._get_user_title())
            user_input = self.session.prompt(
                config.ui.prompt_symbol,
                style=self.style,
            )
            return user_input.strip()
        except KeyboardInterrupt:
            # Handle Ctrl+C
            return "exit"
        except EOFError:
            # Handle Ctrl+D
            return "exit"

    def render_conversation(self, messages: list[BaseMessage], chat_id: str | None):
        self.console.clear()
        # Display welcome message
        self.display_welcome_message()
        chat_name = chat_id if chat_id else "Anonymous chat"

        content = Text(
            f" CONVERSATION START [{chat_name}]",
            style=f"bold black on {config.colors.system}",
        )
        rule = Rule(content, style=f"on {config.colors.system}", characters=" ")

        self.console.print(rule)
        for message in messages:
            message.content = cast(str, message.content)
            if isinstance(message, HumanMessage):
                self.console.print(self._get_user_title())
                self.console.print(
                    f"[{config.colors.user}]{config.ui.prompt_symbol}[/] {message.content}"
                )
            elif isinstance(message, AIMessage):
                self.console.print(self._get_ai_title())
                self.console.print(self._get_markdown(message.content))
                self.console.print()
            else:
                continue

    def _update_live(self):
        text = self._get_markdown(self.current_response)

        content = Group(self._get_ai_title(), text)
        self.live.update(content)

    def stream_token(self, token: str, chunk_type: str):
        """Display a streaming token from the assistant."""
        if not self.streaming:
            self.console.clear()
            self.live.start()
            self.streaming = True
        if chunk_type == "thinking" and not self.thinking:
            self.thinking = True
            self.current_response += "\\<think>\n"
        if chunk_type == "text" and self.thinking:
            # Here starts the actual response, clear the thinking part
            self.thinking = False
            self.current_response = ""

        self.current_response += token
        self._update_live()

    def end_streaming(self):
        """End the streaming response and print a newline."""
        if self.streaming:
            self.live.stop()
            self.console.print()
            self.streaming = False
            self.current_response = ""
