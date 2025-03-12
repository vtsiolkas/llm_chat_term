import shlex
import subprocess

from llm_chat_term.llm.tools.definitions import CatFileCommand
from llm_chat_term.llm.tools.main import register_model


@register_model
def handle_cat(model: CatFileCommand):
    try:
        result = subprocess.run(  # noqa: S603
            ["cat", *shlex.split(model.arguments)],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        return {"success": False, "exception": str(e)}

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "command": f"cat {model.arguments}",
    }
