import os
import sys

from langchain_core.messages import SystemMessage
from pydantic import SecretStr

from llm_chat_term import db, utils
from llm_chat_term.config import ModelConfig, config
from llm_chat_term.llm.insert_commands import parse_insert_commands
from llm_chat_term.llm.llm_client import LLMClient
from llm_chat_term.ui.chat_ui import ChatUI


class LLMChat:
    def __init__(self):
        self.ui = ChatUI()
        available_model: ModelConfig | None = None
        for model in config.llm.models:
            try:
                self.api_key = self._get_api_key(model)
            except ValueError:
                continue
            else:
                available_model = model
                break

        if available_model is None:
            error_msg = (
                "Could not find an API key for any of the providers.\n"
                f"Please add them in {db.get_config_file()} or as an env var\n"
            )
            sys.stderr.write(error_msg)
            sys.exit(1)
        self.model = available_model
        self.chat_id = self.initialize()
        self.client = LLMClient(self.model, self.api_key)
        if self.chat_id:
            self.client.parse_messages(self.chat_id)
            self.ui.render_conversation(self.client.messages, self.chat_id)
        else:
            self.client.messages = [SystemMessage(config.llm.system_prompt)]
            self.ui.render_conversation(self.client.messages, self.chat_id)

    def initialize(self) -> str:
        try:
            chat_id = self.ui.select_chat()
        except Exception as e:
            error_msg = f"Error: {e!s}\n"
            sys.stderr.write(error_msg)
            sys.exit(1)
        return chat_id

    def start_chat(self):
        should_think = False
        should_save = True

        while True:
            # Get user input
            user_input = self.ui.get_user_input(self.model.name, self.chat_id)
            # Skip empty inputs
            if not user_input:
                continue
            # Check for commands
            if user_input in (":exit", "exit"):
                sys.stderr.write("\nExiting...\n")
                break
            if user_input == ":help":
                self.ui.display_help()
                continue
            if user_input == ":info":
                self.ui.display_info(self.chat_id)
                continue
            if user_input in [":edit", ":e"]:
                if self.chat_id:
                    utils.open_in_editor(self.chat_id)
                    self.client.parse_messages(self.chat_id)
                    self.ui.render_conversation(self.client.messages, self.chat_id)
                else:
                    new_chat_id = self.ui.create_new_chat(allow_blank=False)
                    if new_chat_id:
                        messages_dict = self.client.get_conversation_history()
                        db.save_chat_history(new_chat_id, messages_dict)
                        utils.open_in_editor(new_chat_id)
                        self.chat_id = new_chat_id
                        self.client.parse_messages(self.chat_id)
                        self.ui.render_conversation(self.client.messages, self.chat_id)
                    else:
                        sys.stderr.write(
                            "Cannot edit conversation without a chat name...\n"
                        )
                continue
            if user_input == ":model":
                self.model = self.ui.select_model()
                try:
                    self.api_key = self._get_api_key(self.model)
                except ValueError as e:
                    error_msg = f"Error: {e!s}\n"
                    sys.stderr.write(error_msg)
                else:
                    self.client.configure_model(self.model, self.api_key)
                continue
            if user_input == ":chat":
                self.chat_id = self.ui.select_chat()
                self.client.parse_messages(self.chat_id)
                self.ui.render_conversation(self.client.messages, self.chat_id)
                continue
            if user_input == ":redraw":
                self.client.parse_messages(self.chat_id)
                self.ui.render_conversation(self.client.messages, self.chat_id)
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
            self.client.add_user_message(user_input)
            if self.chat_id and should_save:
                db.save_chat_history(
                    self.chat_id, self.client.get_conversation_history()
                )

            # Get and display streaming response
            self.ui.display_loader()
            try:
                response = self.client.get_response(
                    self.ui.stream_token,
                    should_think=should_think,
                )
                if should_save:
                    self.client.add_assistant_message(response)
                    if self.chat_id:
                        db.save_chat_history(
                            self.chat_id, self.client.get_conversation_history()
                        )

            except Exception as e:
                error_msg = f"Somethig went wrong... {e!s}\n"
                sys.stderr.write(error_msg)
            should_think = False
            should_save = True

            # End streaming
            self.ui.end_streaming()

        return sys.exit(0)

    def _get_api_key(self, model: ModelConfig):
        api_key = next(
            (x.api_key for x in config.llm.api_keys if x.provider == model.provider),
            SecretStr(""),
        )
        if not api_key.get_secret_value():
            api_key = os.getenv(f"{model.provider.upper()}_API_KEY", None)
            if not api_key:
                error_msg = (
                    f"API key for model {model} is not set. Please set it in your "
                    f"{db.get_config_file()} file or as an env var."
                )
                raise ValueError(error_msg)
            api_key = SecretStr(api_key)

        return api_key
