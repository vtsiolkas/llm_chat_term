from pydantic import BaseModel, Field


class CatFileCommand(BaseModel):
    """Execute the `cat` command with arbitrary arguments.
    The arguments will be passed through shlex.split().
    Use it to get the contents of one or more files in the current directory.
    Returns a success boolean, the return code, stdout, and stderr of the command as json.
    Example:
    To execute `cat file.txt` call this tool with {"arguments": "file.txt"}
    """

    arguments: str = Field(..., description="The arguments for the cat command")


class GitCommand(BaseModel):
    """Execute the `git` command with arbitrary arguments.
    The arguments will be passed through shlex.split().
    Use it to execute git related commands (e.g. status, diff, add, commit, branch, rebase).
    If some action is destructive(not reversible, e.g. "git checkout file"), don't execute it.
    Returns a success boolean, the return code, stdout, and stderr of the command as json.
    Example:
    To execute `git status -s` call this tool with {"arguments": "status -s"}
    """

    arguments: str = Field(..., description="The arguments for the git command")


# These will be bound to the LLM model
tools = [
    CatFileCommand,
    GitCommand,
]
