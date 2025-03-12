import json
import shlex
import subprocess

from llm_chat_term.llm.tools.definitions import GitCommand
from llm_chat_term.llm.tools.main import register_model


@register_model
def handle_git(model: GitCommand):
    result = subprocess.run(  # noqa: S603
        ["git", *shlex.split(model.arguments)],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    output = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "command": f"git {model.arguments}",
    }
    return json.dumps(output, indent=2)
