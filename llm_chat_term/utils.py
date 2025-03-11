import os
import subprocess

from pydantic import SecretStr

from llm_chat_term import db
from llm_chat_term.config import config


def get_api_key(provider: str) -> SecretStr:
    api_key: SecretStr = next(
        (x.api_key for x in config.llm.api_keys if x.provider == provider),
        SecretStr(""),
    )
    if not api_key.get_secret_value():
        from_env = os.getenv(f"{provider.upper()}_API_KEY", None)
        if not from_env:
            error_msg = (
                f"API key for provider {provider.upper()} is not set. Please set it in your "
                f"{db.get_config_file()} file or as an env var."
            )
            raise ValueError(error_msg)
        api_key = SecretStr(from_env)

    return api_key


def delete_chat(chat_id: str) -> None:
    full_path = db.get_chat_file(chat_id)
    full_path.unlink()


def open_in_editor(chat_id: str):
    full_path = db.get_chat_file(chat_id)
    editor = os.environ.get("EDITOR", "vim")
    # Assume that the user knows what EDITOR is set
    subprocess.call([editor, str(full_path)])  # noqa: S603


def has_audio_support():
    try:
        import pyaudio  # pyright: ignore[reportUnusedImport]  # noqa: F401
        import pydub  # pyright: ignore[reportUnusedImport]  # noqa: F401

    except ImportError:
        return False
    else:
        return True
