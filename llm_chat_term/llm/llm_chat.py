import sys

from langchain_core.messages import SystemMessage
from pydantic import SecretStr

from llm_chat_term import db, utils
from llm_chat_term.audio.audio_entrypoint import handle_voice
from llm_chat_term.config import ModelConfig, config
from llm_chat_term.llm.insert_commands import parse_insert_commands
from llm_chat_term.llm.llm_client import LLMClient
from llm_chat_term.ui.chat_ui import ChatUI


class LLMChat:
    def __init__(self):
        self.ui = ChatUI()
        available_model: ModelConfig | None = None

        self.api_key = SecretStr("")
        for model in config.llm.models:
            try:
                self.api_key = utils.get_api_key(model.provider)
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
        recorded_prompt: str = ""

        while True:
            # Get user input
            user_input = self.ui.get_user_input(
                self.model.name, self.chat_id, prefilled_prompt=recorded_prompt
            )
            recorded_prompt = ""
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
                model = self.ui.select_model()
                try:
                    self.api_key = utils.get_api_key(model.provider)
                except ValueError as e:
                    error_msg = f"Error: {e!s}\n"
                    sys.stderr.write(error_msg)
                else:
                    self.model = model
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
            if user_input == ":agent on":
                self.client.agent_mode = True
                self.ui.console.print("Agent mode enabled", style="bold green")
                continue
            if user_input == ":agent off":
                self.client.agent_mode = False
                self.ui.console.print("Agent mode disabled", style="bold orchid")
                continue
            if user_input.startswith(":think"):
                should_think = True
            elif user_input.startswith(":v"):
                recorded_prompt = handle_voice()
                continue
            else:
                try:
                    user_input = parse_insert_commands(user_input)
                except Exception as e:
                    error_msg = f"Error: {e!s}\n"
                    sys.stderr.write(error_msg)
                    continue

            # Get and display streaming response
            self.ui.display_loader()
            try:
                self.client.get_response(
                    user_input,
                    self.ui.stream_token,
                    chat_id=self.chat_id,
                    should_think=should_think,
                )
            except Exception as e:
                error_msg = f"Something went wrong... {e!s}\n"
                sys.stderr.write(error_msg)
            should_think = False

            # End streaming
            self.ui.end_streaming()

        return sys.exit(0)
