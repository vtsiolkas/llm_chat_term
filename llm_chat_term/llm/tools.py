from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, Field


class GetWeather(BaseModel):
    """Get the current weather in a given location"""

    location: str = Field(..., description="The city, e.g. San Francisco")


tools = [GetWeather]


# Type variables for type safety
T = TypeVar("T", bound=BaseModel)

# Registry to map model names to (model class, handler function) pairs
model_registry: dict[str, tuple[type[BaseModel], Callable[[Any], Any]]] = {}


# Decorator to register models and their handlers
def register_model(model_name: str):
    def decorator(handler_func: Callable[[T], Any]):
        # Get the type annotation of the first parameter
        model_class = handler_func.__annotations__.get("model")
        if not model_class:
            error_msg = (
                f"Handler {handler_func.__name__} must have a typed 'model' parameter"
            )

            raise ValueError(error_msg)

        model_registry[model_name] = (model_class, handler_func)
        return handler_func

    return decorator


# Handler functions with their corresponding model types
@register_model("GetWeather")
def handle_weather(model: GetWeather):
    # Process the weather request
    return f"The weather in {model.location} is rainy with storms."


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
