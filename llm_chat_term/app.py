"""Main application module for the terminal LLM chatbot."""

import signal
import sys
from typing import NoReturn

from llm_chat_term import db, utils
from llm_chat_term.chat_selector import create_new_chat, select_chat
from llm_chat_term.chat_ui import ChatUI
from llm_chat_term.config import config
from llm_chat_term.insert_commands import parse_insert_commands
from llm_chat_term.llm_client import LLMClient
from llm_chat_term.model_selector import select_model


def check_api_key():
    model = config.llm.models[0]
    if not model.api_key.get_secret_value():
        error_msg = (
            "API key for the default model is not set. "
            "Please set it in your config.yaml file."
        )
        raise ValueError(error_msg)


def main() -> NoReturn:
    """Run the terminal LLM chatbot application."""
    try:
        check_api_key()
    except ValueError as e:
        error_msg = f"Error: {e!s}\n"
        sys.stderr.write(error_msg)
        sys.exit(1)

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, utils.signal_handler)

    try:
        selected_chat = select_chat()
    except Exception as e:
        error_msg = f"Error: {e!s}\n"
        sys.stderr.write(error_msg)
        sys.exit(1)

    # Initialize UI and LLM client
    ui = ChatUI()
    llm = LLMClient(ui, selected_chat)
    should_think = False
    should_save = True

    # Main application loop
    while True:
        # Get user input
        user_input = ui.get_user_input(llm.model_config.model, llm.chat_id)
        # Skip empty inputs
        if not user_input:
            continue
        # Check for commands
        if user_input in (":exit", "exit"):
            sys.stderr.write("\nExiting...\n")
            break
        if user_input == ":help":
            ui.display_help()
            continue
        if user_input == ":info":
            ui.display_info(selected_chat)
            continue
        if user_input in [":edit", ":e"]:
            if selected_chat:
                utils.open_in_editor(selected_chat)
                llm.parse_messages()
            else:
                selected_chat = create_new_chat(allow_blank=False)
                if selected_chat:
                    messages_dict = llm.get_conversation_history()
                    db.save_chat_history(selected_chat, messages_dict)
                    utils.open_in_editor(selected_chat)
                    llm.chat_id = selected_chat
                    llm.parse_messages()
                else:
                    sys.stderr.write(
                        "Cannot edit conversation without a chat name...\n"
                    )
            continue
        if user_input == ":model":
            selected_model = select_model()
            llm.configure_model(selected_model)
            continue
        if user_input == ":chat":
            selected_chat = select_chat()
            llm = LLMClient(ui, selected_chat)
            continue
        if user_input == ":redraw":
            llm.parse_messages()
            continue
        if user_input.startswith(":tmp"):
            should_save = False
        elif user_input.startswith(":think"):
            should_think = True
        else:
            try:
                user_input = parse_insert_commands(user_input)
            except Exception as e:
                error_msg = f"Error: {e!s}\n"
                sys.stderr.write(error_msg)
                continue

        # Add message to LLM client
        llm.add_user_message(user_input, should_save=should_save)

        # Get and display streaming response
        try:
            llm.get_response(
                ui.stream_token, should_think=should_think, should_save=should_save
            )
        except Exception as e:
            error_msg = f"Somethig went wrong... {e!s}\n"
            sys.stderr.write(error_msg)
        should_think = False
        should_save = True

        # End streaming
        ui.end_streaming()

    return sys.exit(0)


if __name__ == "__main__":
    main()
