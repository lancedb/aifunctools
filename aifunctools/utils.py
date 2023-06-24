import inspect
from typing import Callable

from pydantic import BaseModel, create_model


def function_to_model(function: Callable) -> BaseModel:
    """
    Converts a function's arguments into a pydantic model.
    All arguments must have valid type annotations.

    inspired by Marvin (but installation is too heavy for this project)
    """
    signature = inspect.signature(function)

    fields = {
        p: (
            signature.parameters[p].annotation,
            (
                signature.parameters[p].default
                if signature.parameters[p].default != inspect._empty
                else ...
            ),
        )
        for p in signature.parameters
        if p != getattr(function, "__self__", None)
    }

    # Create Pydantic model
    try:
        model = create_model(function.__name__, **fields)
    except RuntimeError as exc:
        if "see `arbitrary_types_allowed` " in str(exc):
            raise ValueError(
                f"Error while inspecting {function.__name__} with signature"
                f" {signature}: {exc}"
            )
        else:
            raise

    return model


def schema_properties_to_json(properties):
    """
    Convert "properties" from a pydantic model json schema
    to OpenAI json schema
    """
    properties = {
        name: {k: v for k, v in prop.items() if k != "title"}
        for name, prop in properties.items()
    }
    return properties
