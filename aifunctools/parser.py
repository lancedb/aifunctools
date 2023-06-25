"""
Function parser
"""
import json
from functools import wraps
from inspect import signature
from typing import Callable, Any, Optional

from docstring_parser import parse
from pydantic import BaseModel, validate_arguments


from aifunctools.utils import function_to_model, schema_properties_to_json


class FunctionParameterDescriptor(BaseModel):
    type: str
    description: str


class OpenAIFunction:

    @classmethod
    def from_function(cls, func: Callable) -> "OpenAIFunction":
        descriptor, validated = parse_function(func)
        return cls(validated, **descriptor)

    def __init__(self, validated,
                 name: str,
                 description: str = None,
                 parameters: list[dict] = None) -> None:
        self.validated = validated
        self.name = name
        self.description = description
        self.parameters = parameters

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        @wraps(self.validated.raw_function)
        def wrapper(*args, **kwargs):
            return self.validated(*args, **kwargs)

        return wrapper(*args, **kwargs)

    def to_openai_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    def from_openai_response(self, response: dict):
        for c in response["choices"]:
            if c["finish_reason"] == "function_call":
                msg = c["message"]
                # find and evaluate the function call
                func_data = msg["function_call"]
                name = func_data["name"]
                if name == self.name:
                    args = json.loads(func_data["arguments"])
                    result = self(**args)
                    return result


def parse_function(func: Callable):
    """
    Parse the docstring and type annotations
    to automatically create a signature for GPT functions

    :param func: Callable
    :return:
    """
    model = function_to_model(func)
    schema = model.model_json_schema()
    docs = parse(func.__doc__)
    param_docs = {p.arg_name: p.description for p in docs.params}
    desc = ""
    if docs.short_description:
        desc += docs.short_description
    if docs.long_description:
        desc += "\n\n" + docs.long_description

    properties = schema_properties_to_json(schema["properties"])
    for name, prop in properties.items():
        prop["description"] = param_docs.get(name, "")

    descriptor = {
            "name": func.__name__,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": schema.get("required", [])
            }
        }
    return descriptor, validate_arguments(func)
