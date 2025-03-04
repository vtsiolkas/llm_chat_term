import os
import mimetypes


def process_read_commands(user_input: str) -> str:
    result_lines: list[str] = []

    for line in user_input.splitlines():
        if line.strip().startswith(":read "):
            # Extract the file path
            file_path = line.strip()[6:].strip()

            # Check if file exists
            if not os.path.exists(file_path):
                result_lines.append(f"Error: File not found: {file_path}")
                continue

            # Check if file is binary
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and not mime_type.startswith(("text/", "application/json")):
                raise Exception(f"Error: :read file appears to be binary: {file_path}")

            try:
                # Try to read the file
                with open(file_path, "r", encoding="utf-8") as f:
                    file_contents = f.read()
                # Add file contents instead of the :read line
                result_lines.append(file_contents.rstrip())
            except UnicodeDecodeError:
                raise Exception(f"Error: :read file appears to be binary: {file_path}")
            except Exception as e:
                raise Exception(f"Error: Could not :read file: {file_path}: {str(e)}")
        else:
            # Keep the original line
            result_lines.append(line)

    return "\n".join(result_lines)
