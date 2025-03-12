from pydantic import BaseModel, Field


class GetWeather(BaseModel):
    """Get the current weather in a given location"""

    location: str = Field(..., description="The city, e.g. San Francisco")


class CatFileCommand(BaseModel):
    """Execute the `cat` command with arbitrary arguments
    Returns the return code, stdout, and stderr of the command
    Example:
    To execute `cat file.txt` call this tool with {"arguments": "file.txt"}
    """

    arguments: str = Field(..., description="The arguments for the cat command")


class GitCommand(BaseModel):
    """Execute the `git` command with arbitrary arguments
    Returns the return code, stdout, and stderr of the command
    If some action is destructive, don't execute it.
    Example:
    To execute `git status -s` call this tool with {"arguments": "status -s"}
    """

    arguments: str = Field(..., description="The arguments for the git command")


tools = [GetWeather, CatFileCommand, GitCommand]
