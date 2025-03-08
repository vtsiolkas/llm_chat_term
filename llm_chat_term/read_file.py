import mimetypes
from pathlib import Path

from llm_chat_term.exceptions import FileReadError


def process_read_commands(user_input: str) -> str:
    result_lines: list[str] = []

    for line in user_input.splitlines():
        if line.strip().startswith(":read "):
            # Extract the file path
            file_path = Path(line.strip()[6:])
            file_path = file_path.expanduser()

            # Check if file exists
            if not file_path.exists():
                error_msg = f"Error: File not found: {file_path}"
                raise FileReadError(error_msg)

            # Check if file is binary
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and not mime_type.startswith(("text/", "application/json")):
                error_msg = f"Error: :read file appears to be binary: {file_path}"
                raise FileReadError(error_msg)

            try:
                # Try to read the file
                with file_path.open(encoding="utf-8") as f:
                    file_contents = f.read()
                # Add file contents instead of the :read line
                result_lines.append(file_contents.rstrip())
            except UnicodeDecodeError as e:
                error_msg = ()
                raise FileReadError(error_msg) from e
            except Exception as e:
                error_msg = f"Error: Could not :read file: {file_path}: {e!s}"
                raise FileReadError(error_msg) from e
        else:
            # Keep the original line
            result_lines.append(line)

    return "\n".join(result_lines)
