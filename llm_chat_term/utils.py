import os
import subprocess
import sys
from typing import Any

from llm_chat_term import db


def signal_handler(_sig: Any, _frame: Any):
    """Handle Ctrl+C to exit gracefully."""
    print("\nExiting...")
    sys.exit(0)


def delete_chat(chat_id: str) -> None:
    full_path = db.get_chat_file(chat_id)
    os.remove(full_path)


def open_in_editor(chat_id: str):
    full_path = db.get_chat_file(chat_id)
    editor = os.environ.get("EDITOR", "vim")
    subprocess.call([editor, str(full_path)])
