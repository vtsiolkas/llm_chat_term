"""LLM client for the terminal chatbot using LangChain."""

import json
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
    ToolMessage,
    ToolMessageChunk,
    message_chunk_to_message,
)
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from llm_chat_term import db
from llm_chat_term.config import ModelConfig, config
from llm_chat_term.llm.tools.definitions import tools
from llm_chat_term.llm.tools.main import TOOL_REFUSAL, process_tool_request
from llm_chat_term.ui.chat_ui import ChatUI


def get_chunk_text_and_type(chunk: BaseMessageChunk) -> tuple[str, str]:
    """Get the text content and type of the message."""
    if isinstance(chunk.content, str):
        return chunk.content, "text"

    # must be a list, extract the type from the first block
    content: list[dict[str, str] | str] = chunk.content
    first_block = content[0]
    if isinstance(first_block, str):
        chunk_type = "text"
    else:
        chunk_type: str = first_block.get("type", "text")
    return "".join(
        block if isinstance(block, str) else block.get(chunk_type, "")
        for block in chunk.content  # pyright: ignore[reportUnknownVariableType]
    ), chunk_type


class LLMClient:
    """Client for interacting with the LLM."""

    agent_mode = False

    def __init__(self, model: ModelConfig, api_key: SecretStr):
        """Initialize the LLM client with the configured model."""
        self.messages: list[BaseMessage] = []
        self.configure_model(model, api_key)

    def configure_model(self, model_config: ModelConfig, api_key: SecretStr) -> None:
        self.model_config = model_config
        if model_config.provider == "openai" and model_config.name.startswith("o"):
            temperature = 1.0
        else:
            temperature = model_config.temperature or 0.4
        temperature = 1.0
        if model_config.provider == "anthropic":
            self.model = ChatAnthropic(  # pyright: ignore[reportCallIssue]
                api_key=api_key,
                model=model_config.name,  # pyright: ignore[reportCallIssue]
                temperature=temperature,
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                stream_usage=False,
                streaming=True,
            )
            self.thinking_model = ChatAnthropic(  # pyright: ignore[reportCallIssue]
                api_key=api_key,
                model=model_config.name,  # pyright: ignore[reportCallIssue]
                temperature=1.0,  # Needs to be 1 for thinking
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                thinking={"type": "enabled", "budget_tokens": 2048},
                stream_usage=False,
                streaming=True,
            )
        elif model_config.provider == "openai":
            self.model = ChatOpenAI(
                api_key=api_key,
                model=model_config.name,
                temperature=temperature,
                max_tokens=16384,  # pyright: ignore[reportCallIssue]
                streaming=True,
            )
            self.thinking_model = self.model

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.messages.append(HumanMessage(content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append(AIMessage(content))

    def get_response(
        self,
        user_message: str,
        stream_callback: Callable[[str, str], None],
        *,
        chat_id: str = "",
        should_think: bool = False,
        # For :tmp handling, we don't append user message to conversation history
        # but we only send it for the current response
    ) -> None:
        """Get a response from the LLM and stream it through the callback."""
        if self.agent_mode:
            model = self.model.bind_tools(tools)
        else:
            # Thinking model only for claude, o3-mini always thinks, 4o never
            model = self.thinking_model if should_think else self.model
        model = cast(BaseChatModel, model)

        response = ""
        if user_message:
            self.messages.append(HumanMessage(user_message))
        is_tool = False
        tool_json = ""
        tool_name = ""
        tool_call_id = ""
        tool_message: BaseMessageChunk | None = None
        # TODO: o3-mini doesn't know what to do with response ToolMessage
        # Ditch langchain
        for chunk in model.stream(self.messages):
            if (
                hasattr(chunk, "tool_call_chunks")
                and isinstance(chunk.tool_call_chunks, list)
                and len(chunk.tool_call_chunks) > 0
                and isinstance(chunk.tool_call_chunks[0], dict)
            ):
                chunk = cast(ToolMessageChunk, chunk)
                block = cast(dict[str, str], chunk.tool_call_chunks[0])
                if not is_tool:
                    is_tool = True
                    tool_name = block["name"]
                    tool_call_id = block["id"]
                    tool_message = chunk
                else:
                    tool_json += block["args"]
                    if tool_message:
                        tool_message = tool_message + chunk
            else:
                text, chunk_type = get_chunk_text_and_type(chunk)
                stream_callback(text, chunk_type)
                response += chunk.text()
        if is_tool and tool_message and tool_call_id:
            ai_tool_message = message_chunk_to_message(tool_message)
            # Pause streaming to display the confirm prompt
            stream_callback("", "prompt_tool")
            confirm = ChatUI.display_prompt(f"Use tool {tool_name} with {tool_json}:")
            if confirm:
                stream_callback(
                    (f"\n\n*-- Calling tool {tool_name} with {tool_json}...*\n"),
                    "text",
                )
                tool_result = process_tool_request(tool_name, json.loads(tool_json))
                stream_callback(
                    f"{'**success**' if tool_result['success'] else '**failure**'}\n\n",
                    "text",
                )
                self.messages.append(ai_tool_message)
                self.messages.append(
                    ToolMessage(json.dumps(tool_result), tool_call_id=tool_call_id)
                )
                self.get_response("", stream_callback, chat_id=chat_id)
            else:
                stream_callback((f"\n\n-- Will not call tool {tool_name}.\n\n"), "text")
                self.messages.append(ai_tool_message)
                self.messages.append(
                    ToolMessage(TOOL_REFUSAL, tool_call_id=tool_call_id)
                )

        self.messages.append(AIMessage(response))
        if chat_id:
            db.save_chat_history(chat_id, self.get_conversation_history())

    def parse_messages(self, chat_id: str):
        messages_dict = db.load_chat_history(chat_id)
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
            db.save_chat_history(chat_id, self.get_conversation_history())

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
