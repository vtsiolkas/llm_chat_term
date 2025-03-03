"""Main application module for the terminal LLM chatbot."""

import signal
import sys
from typing import NoReturn

from llm_chat_term import utils
from llm_chat_term.chat_selector import select_chat
from llm_chat_term.chat_ui import ChatUI
from llm_chat_term.llm_client import LLMClient
from llm_chat_term.config import config


def main() -> NoReturn:
    """Run the terminal LLM chatbot application."""
    try:
        if config.llm.provider == "anthropic":
            if not config.llm.anthropic_key:
                raise ValueError(
                    "Anthropic API key is not set. Please set it in your config.yaml file."
                )
        elif config.llm.provider == "openai":
            if not config.llm.openai_api_key:
                raise ValueError(
                    "OpenAI API key is not set. Please set it in your config.yaml file."
                )
        else:
            raise ValueError(f"Invalid provider: {config.llm.provider}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, utils.signal_handler)

    try:
        selected_chat = select_chat()
    except Exception as e:
        print("Exiting...", e)
        sys.exit(1)

    # Initialize UI and LLM client
    ui = ChatUI()
    llm = LLMClient(ui, selected_chat)
    should_think = False

    # Main application loop
    while True:
        # Get user input
        user_input = ui.get_user_input()
        # Skip empty inputs
        if not user_input:
            continue
        # Check for commands
        if user_input in ("/exit", "exit"):
            print("Exiting...")
            break
        elif user_input == "/help":
            ui.display_help()
            continue
        elif user_input == "/info":
            ui.display_info(selected_chat)
            continue
        elif user_input in ["/edit", "/e"]:
            if selected_chat:
                utils.open_in_editor(selected_chat)
                llm.parse_messages()
            else:
                print("Cannot edit messages in anonymous chat.")
            continue
        elif user_input == "/select":
            selected_chat = select_chat()
            llm = LLMClient(ui, selected_chat)
            continue
        elif user_input == "/redraw":
            llm.parse_messages()
            continue
        elif user_input.startswith("/think"):
            should_think = True

        # Add message to LLM client
        llm.add_user_message(user_input)

        # Get and display streaming response
        llm.get_response(ui.stream_token, should_think)
        should_think = False

        # End streaming
        ui.end_streaming()

    return sys.exit(0)


if __name__ == "__main__":
    main()
