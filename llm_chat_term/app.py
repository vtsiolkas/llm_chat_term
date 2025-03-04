"""Main application module for the terminal LLM chatbot."""

import signal
import sys
from typing import NoReturn

from llm_chat_term import utils
from llm_chat_term.chat_selector import select_chat
from llm_chat_term.chat_ui import ChatUI
from llm_chat_term.llm_client import LLMClient
from llm_chat_term.config import config
from llm_chat_term.model_selector import select_model
from llm_chat_term.read_file import process_read_commands


def main() -> NoReturn:
    """Run the terminal LLM chatbot application."""
    try:
        model = config.llm.models[0]
        if not model.api_key.get_secret_value():
            raise ValueError(
                "API key for the default model is not set. Please set it in your config.yaml file."
            )
    except Exception as e:
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
        if user_input in (":exit", "exit"):
            print("Exiting...")
            break
        elif user_input == ":help":
            ui.display_help()
            continue
        elif user_input == ":info":
            ui.display_info(selected_chat)
            continue
        elif user_input in [":edit", ":e"]:
            if selected_chat:
                utils.open_in_editor(selected_chat)
                llm.parse_messages()
            else:
                print("Cannot edit messages in anonymous chat.")
            continue
        elif user_input == ":model":
            selected_model = select_model()
            llm.configure_model(selected_model)
            continue
        elif user_input == ":chat":
            selected_chat = select_chat()
            llm = LLMClient(ui, selected_chat)
            continue
        elif user_input == ":redraw":
            llm.parse_messages()
            continue
        elif user_input.startswith(":think"):
            should_think = True
        else:
            try:
                user_input = process_read_commands(user_input)
            except Exception as e:
                print(e)
                continue

        # Add message to LLM client
        llm.add_user_message(user_input)

        # TODO: Handle errors from LLM API gracefully
        # Get and display streaming response
        llm.get_response(ui.stream_token, should_think)
        should_think = False

        # End streaming
        ui.end_streaming()

    return sys.exit(0)


if __name__ == "__main__":
    main()
