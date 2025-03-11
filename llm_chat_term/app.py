"""Main application module for the terminal LLM chatbot."""

from typing import NoReturn

from llm_chat_term.llm.llm_chat import LLMChat


def main() -> NoReturn:
    """Run the terminal LLM chatbot application."""

    chat = LLMChat()
    chat.start_chat()


if __name__ == "__main__":
    main()
