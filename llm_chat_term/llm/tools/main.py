import json
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

TOOL_REFUSAL = json.dumps({"success": False, "reason": "User refused to allow tool"})

# Type variables for type safety
T = TypeVar("T", bound=BaseModel)

# Registry to map model names to (model class, handler function) pairs
_model_registry: dict[str, tuple[type[BaseModel], Callable[[Any], Any]]] = {}


def get_model_registry():
    return _model_registry


# Decorator to register models handlers
def register_model(handler_func: Callable[[T], Any]):
    # Get the type annotation of the model parameter
    model_class = handler_func.__annotations__.get("model")
    if not model_class:
        error_msg = (
            f"Handler {handler_func.__name__} must have a typed 'model' parameter"
        )

        raise ValueError(error_msg)

    registry = get_model_registry()
    registry[model_class.__name__] = (model_class, handler_func)
    return handler_func


# Function to process incoming requests
def process_tool_request(model_name: str, data: dict[str, Any]):
    registry = get_model_registry()
    if model_name not in registry:
        error_msg = f"Unknown tool: {model_name}"
        raise ValueError(error_msg)

    model_class, handler_func = registry[model_name]

    # Instantiate the model with the provided data
    model_instance = model_class(**data)

    # Call the handler with the model instance
    return handler_func(model_instance)
