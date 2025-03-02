"""LLM client for the terminal chatbot using LangChain."""

from typing import Any, Callable, cast, override

from langchain.callbacks.base import BaseCallbackHandler
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from llm_chat_term import db
from llm_chat_term.chat_ui import ChatUI
from llm_chat_term.config import config


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, stream_callback: Callable[[str], None]):
        """Initialize with a callback function that will be called with each token."""
        self.stream_callback = stream_callback

    @override
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Pass the token to the callback function."""
        self.stream_callback(token)


class LLMClient:
    """Client for interacting with the LLM."""

    def __init__(self, ui: ChatUI, chat_id: str | None):
        """Initialize the LLM client with the configured model."""
        if config.llm.provider == "anthropic":
            self.model = ChatAnthropic(  # pyright: ignore[reportCallIssue]
                api_key=config.llm.anthropic_key,
                model=config.llm.model,  # pyright: ignore[reportCallIssue]
                temperature=config.llm.temperature,
                max_tokens=16389,  # pyright: ignore[reportCallIssue]
                streaming=True,
            )
        elif config.llm.provider == "openai":
            self.model = ChatOpenAI(
                api_key=config.llm.openai_api_key,
                model=config.llm.model,
                temperature=config.llm.temperature,
                max_tokens=16389,  # pyright: ignore[reportCallIssue]
                streaming=True,
            )

        self.ui = ui
        self.chat_id: str | None = chat_id
        if chat_id:
            self.parse_messages()
        else:
            self.messages: list[BaseMessage] = [SystemMessage(config.llm.system_prompt)]
            self.ui.render_conversation(self.messages, self.chat_id)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.messages.append(HumanMessage(content))
        if self.chat_id is not None:
            db.save_chat_history(self.chat_id, self.get_conversation_history())

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append(AIMessage(content))
        if self.chat_id is not None:
            db.save_chat_history(self.chat_id, self.get_conversation_history())

    def get_response(self, stream_callback: Callable[[str], None]) -> None:
        """Get a response from the LLM and stream it through the callback."""
        callback_handler = StreamingCallbackHandler(stream_callback)

        response = self.model.invoke(
            self.messages,
            config={
                "callbacks": [callback_handler],
            },
        )
        response.content = cast(str, response.content)
        self.add_assistant_message(response.content)

    def parse_messages(self):
        self.chat_id = cast(str, self.chat_id)
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
