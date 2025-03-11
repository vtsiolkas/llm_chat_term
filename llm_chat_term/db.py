import os
from pathlib import Path
from urllib.parse import quote_plus, unquote_plus

MESSAGE_INDICATOR = "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒"


def get_chat_file(chat_id: str) -> Path:
    return _get_chats_dir() / _encode_filename(chat_id)


def get_config_file() -> Path:
    return _get_config_dir() / "config.yaml"


def _get_config_dir() -> Path:
    """Get platform-specific config directory for llm_chat_term."""
    home = Path.home()

    if os.name == "nt":  # Windows
        config_dir = home / "AppData" / "Local" / "llm_chat_term"
    elif os.name == "posix":  # Linux, macOS, etc.
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / "llm_chat_term"
        elif (home / ".config").exists():
            config_dir = home / ".config" / "llm_chat_term"
        else:  # macOS fallback
            config_dir = home / "Library" / "Preferences" / "llm_chat_term"
    else:
        config_dir = home / ".llm_chat_term"  # Fallback

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _get_data_dir() -> Path:
    """Get platform-specific data directory for llm_chat_term."""
    home = Path.home()

    if os.name == "nt":  # Windows
        data_dir = home / "AppData" / "Local" / "llm_chat_term"
    elif os.name == "posix":  # Linux, macOS, etc.
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            data_dir = Path(xdg_data_home) / "llm_chat_term"
        elif (home / ".local" / "share").exists():  # Linux
            data_dir = home / ".local" / "share" / "llm_chat_term"
        else:  # macOS
            data_dir = home / "Library" / "Application Support" / "llm_chat_term"
    else:
        data_dir = home / ".llm_chat_term"  # Fallback

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _get_chats_dir() -> Path:
    """Get the directory where the chats are saved"""
    chats_dir = _get_data_dir() / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)
    return chats_dir


def _encode_filename(chat_id: str) -> str:
    """Encode chat ID to a safe filename."""
    return f"{quote_plus(chat_id)}.txt"


def _decode_filepath(file_path: Path) -> str:
    """Decode filename back to original chat ID."""
    # Remove .txt extension and decode
    return unquote_plus(file_path.stem)


# TODO: Sometimes we get a ".txt" file in the chats dir
# Investigate
def save_chat_history(chat_id: str, messages: list[dict[str, str]]):
    """Save chat history to a text file.

    Args:
        chat_id: Identifier for the chat session
        messages: List of message dictionaries
    """
    file_path = get_chat_file(chat_id)

    with file_path.open("w", encoding="utf-8") as f:
        max_role_width = max([len(message["role"]) for message in messages])
        for message in messages:
            role = message["role"]
            padding = max_role_width - len(role)
            left_padding = padding // 2
            right_padding = padding - left_padding
            padded_role = " " * left_padding + role + " " * right_padding

            f.write(f"{MESSAGE_INDICATOR} {padded_role} {MESSAGE_INDICATOR}\n")
            f.write(f"{message['content']}\n")


def load_chat_history(chat_id: str) -> list[dict[str, str]]:
    """Load chat history from a text file.

    Args:
        chat_id: Identifier for the chat session

    Returns:
        List of message dictionaries
    """
    file_path = get_chat_file(chat_id)

    if not file_path.exists():
        return []

    messages: list[dict[str, str]] = []
    with file_path.open(encoding="utf-8") as f:
        lines = f.read().splitlines()
        last_index = len(lines) - 1

        msg_role = ""
        msg_content = ""
        for i, line in enumerate(lines):
            if line.startswith(f"{MESSAGE_INDICATOR}") and line.endswith(
                f"{MESSAGE_INDICATOR}"
            ):
                messages.append(
                    {
                        "role": msg_role,
                        "content": msg_content.rstrip(),
                    }
                )
                msg_content = ""
                # Extract next message type if not last file line
                msg_role = line.split(f"{MESSAGE_INDICATOR}")[1].strip()
            elif i == last_index:
                msg_content += line + "\n"
                messages.append(
                    {
                        "role": msg_role,
                        "content": msg_content.rstrip(),
                    }
                )
            else:
                msg_content += line + "\n"

    return messages


def list_all_chats() -> list[str]:
    """List all available chat histories.

    Returns:
        List of all chat_ids
    """
    data_dir = _get_chats_dir()
    chats_with_time: list[tuple[str, float]] = []

    for file_path in data_dir.glob("*.txt"):
        try:
            chat_id = _decode_filepath(file_path)
            mod_time = file_path.stat().st_mtime
            chats_with_time.append((chat_id, mod_time))
        except Exception:
            # Skip files that can't be decoded properly
            continue

    chats_with_time.sort(key=lambda x: x[1], reverse=True)

    return [chat_id for chat_id, _ in chats_with_time]
