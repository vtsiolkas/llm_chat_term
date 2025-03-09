import mimetypes
import sys
from pathlib import Path

import trafilatura
from pydantic import HttpUrl

from llm_chat_term.exceptions import FileReadError, UrlReadError


def parse_insert_commands(user_input: str) -> str:
    result_lines: list[str] = []

    for line in user_input.splitlines():
        if line.strip().startswith(":read "):
            # Extract the file path
            file_path = Path(line.strip()[6:])
            file_path = file_path.expanduser()
            sys.stdout.write(f"Embedding file: {file_path}\n")

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
                error_msg = f"Error: :read file appears to be binary: {file_path}"
                raise FileReadError(error_msg) from e
            except Exception as e:
                error_msg = f"Error: Could not :read file: {file_path}: {e!s}"
                raise FileReadError(error_msg) from e
        elif line.strip().startswith(":web "):
            url = line.strip()[5:]
            sys.stdout.write(f"Embedding url: {url}\n")
            try:
                url = HttpUrl(url)
            except ValueError as e:
                error_msg = f"Error: Could not parse url {url}"
                raise UrlReadError(error_msg) from e

            try:
                downloaded = trafilatura.fetch_url(str(url))
                error_msg = f"Error: Could not :web url: {url}"
                if downloaded:
                    text = trafilatura.extract(
                        downloaded,
                        with_metadata=True,
                        deduplicate=True,
                    )
                    if not text:
                        raise UrlReadError(error_msg)
                    result_lines.append(
                        f"The following text was extracted from {url}:\n{text}"
                    )
                    continue

                raise UrlReadError(error_msg)
            except Exception as e:
                error_msg = f"Error: Could not :web url: {url}: {e!s}"
                raise UrlReadError(error_msg) from e

        else:
            # Keep the original line
            result_lines.append(line)

    return "\n".join(result_lines)
