import json
from inspect import signature
import os

from docstring_parser import parse
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-3.5-turbo-0613"


def complete_with_functions(question, *functions):
    """
    Call the openai completion function with specified functions
    to be called optionally. The function signatures can be parsed
    automatically.

    :param question:
    :param functions:
    :return:
    """
    # TODO extend to parsing openapi docs
    req = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": question}
        ],
        "functions": [parse_function(f) for f in functions]
    }
    response = openai.ChatCompletion.create(**req)
    if not any([c["finish_reason"] == "function_call"
                for c in response["choices"]]):
        return response

    messages = call_functions(response, *functions)
    req["messages"].extend(messages)
    return openai.ChatCompletion.create(**req)


def call_functions(response, *functions):
    """
    Make the actual functions using the initial responses

    :param response:
    :param functions:
    :return:
    """
    messages = []
    for c in response["choices"]:
        if c["finish_reason"] == "function_call":
            msg = c["message"]
            messages.append(msg)
            func_data = msg["function_call"]
            args = json.loads(func_data["arguments"])
            name = func_data["name"]
            for f in functions:
                if f.__name__ == name:
                    result = f(**args)
                    messages.append({"role": "function", "name": name, "content": json.dumps(result)})
    return messages


def parse_annotation(annotation):
    """
    Convert the type annotation to type string for json

    :param annotation:
    :return:
    """
    # TODO how to reliably map python type hint to json type?
    return {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean"
    }[annotation.__name__]


def parse_parameter(annotation, docs):
    """
    Convert the parameter signature and docstring
    to json for function api

    :param annotation:
    :param docs:
    :return:
    """
    type_name = parse_annotation(annotation)
    return {
        "type": type_name,
        "description": docs.description if docs is not None else ""
    }


def parse_function(func):
    """
    Parse the docstring and type annotations
    to automatically create a signature for GPT functions

    :param func:
    :return:
    """
    docs = parse(func.__doc__)
    param_docs = {p.arg_name: p for p in docs.params}
    sig = signature(func)
    required = [k for k, v in sig.parameters.items()
                if v.kind == v.POSITIONAL_OR_KEYWORD]

    properties = {
        name: parse_parameter(p.annotation, param_docs.get(name))
        for name, p in sig.parameters.items()
    }
    descriptor = {
            "name": func.__name__,
            "description": docs.short_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    return descriptor