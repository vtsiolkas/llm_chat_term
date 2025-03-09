"""Main application module for the terminal LLM chatbot."""

import signal
from typing import NoReturn

from llm_chat_term import utils
from llm_chat_term.llm.llm_chat import LLMChat


def main() -> NoReturn:
    """Run the terminal LLM chatbot application."""
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, utils.signal_handler)

    chat = LLMChat()
    chat.start_chat()


if __name__ == "__main__":
    main()
