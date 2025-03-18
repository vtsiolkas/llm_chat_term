import shlex
import subprocess

from llm_chat_term.llm.tools.definitions import GitCommand
from llm_chat_term.llm.tools.main import register_model


@register_model
def handle_git(model: GitCommand):
    try:
        result = subprocess.run(  # noqa: S603
            ["git", *shlex.split(model.arguments)],  # noqa: S607
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
        "command": f"git {model.arguments}",
    }
