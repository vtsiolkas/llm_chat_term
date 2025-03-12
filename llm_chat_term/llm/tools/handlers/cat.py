import json
import shlex
import subprocess

from llm_chat_term.llm.tools.definitions import CatFileCommand
from llm_chat_term.llm.tools.main import register_model


@register_model
def handle_cat(model: CatFileCommand):
    result = subprocess.run(  # noqa: S603
        ["cat", *shlex.split(model.arguments)],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    output = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "command": f"cat {model.arguments}",
    }
    return json.dumps(output, indent=2)
