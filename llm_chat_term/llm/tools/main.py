import json
import shlex
import subprocess
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from llm_chat_term.llm.tools.definitions import CatFileCommand, GetWeather, GitCommand

# Type variables for type safety
T = TypeVar("T", bound=BaseModel)

# Registry to map model names to (model class, handler function) pairs
model_registry: dict[str, tuple[type[BaseModel], Callable[[Any], Any]]] = {}


# Decorator to register models handlers
def register_model(handler_func: Callable[[T], Any]):
    # Get the type annotation of the model parameter
    model_class = handler_func.__annotations__.get("model")
    if not model_class:
        error_msg = (
            f"Handler {handler_func.__name__} must have a typed 'model' parameter"
        )

        raise ValueError(error_msg)

    model_registry[model_class.__name__] = (model_class, handler_func)
    return handler_func


# Function to process incoming requests
def process_tool_request(model_name: str, data: dict[str, Any]):
    if model_name not in model_registry:
        error_msg = f"Unknown tool: {model_name}"
        raise ValueError(error_msg)

    model_class, handler_func = model_registry[model_name]

    # Instantiate the model with the provided data
    model_instance = model_class(**data)

    # Call the handler with the model instance
    return handler_func(model_instance)


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


@register_model
def handle_weather(model: GetWeather):
    return f"The weather in {model.location} is rainy with storms."
