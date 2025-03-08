"""LLM client for the terminal chatbot using LangChain."""

from collections.abc import Callable
from typing import cast

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    BaseMessageChunk,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI

from llm_chat_term import db
from llm_chat_term.chat_ui import ChatUI
from llm_chat_term.config import ModelConfig, config


def get_chunk_text_and_type(chunk: BaseMessageChunk) -> tuple[str, str]:
    """Get the text content and type of the message."""
    if isinstance(chunk.content, str):  # pyright: ignore[reportUnknownMemberType]
        return chunk.content, "text"

    # must be a list, extract the type from the first block
    content: list[dict[str, str] | str] = chunk.content
    first_block = content[0]
    if isinstance(first_block, str):
        chunk_type = "text"
    else:
        chunk_type: str = first_block.get("type", "text")
    return "".join(
        block if isinstance(block, str) else block.get(chunk_type, "text")
        for block in chunk.content
    ), chunk_type


class LLMClient:
    """Client for interacting with the LLM."""

    model = None
    thinking_model = None

    def __init__(self, ui: ChatUI, chat_id: str):
        """Initialize the LLM client with the configured model."""
        self.configure_model(config.llm.models[0])

        self.ui = ui
        self.chat_id = chat_id
        if chat_id:
            self.parse_messages()
        else:
            self.messages: list[BaseMessage] = [SystemMessage(config.llm.system_prompt)]
            self.ui.render_conversation(self.messages, self.chat_id)

    def configure_model(self, model_config: ModelConfig) -> None:
        self.model_config = model_config
        if model_config.provider == "openai" and model_config.model.startswith("o"):
            temperature = 1.0
        else:
            temperature = model_config.temperature or 0.4
        if model_config.provider == "anthropic":
            self.model = ChatAnthropic(  # pyright: ignore[reportCallIssue]
                api_key=model_config.api_key,
                model=model_config.model,  # pyright: ignore[reportCallIssue]
                temperature=temperature,
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                stream_usage=False,
                streaming=True,
            )
            self.thinking_model = ChatAnthropic(  # pyright: ignore[reportCallIssue]
                api_key=model_config.api_key,
                model=model_config.model,  # pyright: ignore[reportCallIssue]
                temperature=1.0,  # Needs to be 1 for thinking
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                thinking={"type": "enabled", "budget_tokens": 2048},
                stream_usage=False,
                streaming=True,
            )
        elif model_config.provider == "openai":
            self.model = ChatOpenAI(
                api_key=model_config.api_key,
                model=model_config.model,
                temperature=temperature,
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                streaming=True,
            )
            self.thinking_model = self.model

    def add_user_message(self, content: str, *, should_save: bool = True) -> None:
        """Add a user message to the conversation history."""
        self.messages.append(HumanMessage(content))
        if self.chat_id and should_save:
            db.save_chat_history(self.chat_id, self.get_conversation_history())

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append(AIMessage(content))
        if self.chat_id:
            db.save_chat_history(self.chat_id, self.get_conversation_history())

    def get_response(
        self,
        stream_callback: Callable[[str, str], None],
        *,
        should_think: bool = False,
        should_save: bool = True,
    ) -> None:
        """Get a response from the LLM and stream it through the callback."""
        model = self.thinking_model if should_think else self.model
        model = cast(BaseChatModel, model)

        response = ""
        self.ui.display_loader()
        for chunk in model.stream(self.messages):
            text, chunk_type = get_chunk_text_and_type(chunk)
            stream_callback(text, chunk_type)
            response += chunk.text()
        if should_save:
            self.add_assistant_message(response)

    def parse_messages(self):
        messages_dict = db.load_chat_history(self.chat_id)
        self.messages = []
        for message in messages_dict:
            if message["role"] == "system":
                self.messages.append(SystemMessage(message["content"]))
            elif message["role"] == "user":
                self.messages.append(HumanMessage(message["content"]))
            elif message["role"] == "assistant":
                self.messages.append(AIMessage(message["content"]))

        if not any(isinstance(message, SystemMessage) for message in self.messages):
            self.messages.insert(0, SystemMessage(config.llm.system_prompt))
            db.save_chat_history(self.chat_id, self.get_conversation_history())

        self.ui.render_conversation(self.messages, self.chat_id)

    def get_conversation_history(self) -> list[dict[str, str]]:
        """Get the conversation history as a list of dictionaries."""
        history: list[dict[str, str]] = []

        for message in self.messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                continue

            message.content = cast(str, message.content)
            history.append(
                {
                    "role": role,
                    "content": message.content,
                }
            )

        return history
