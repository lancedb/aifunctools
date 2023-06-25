import json
import os

import openai

from aifunctools.parser import OpenAIFunction

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
    registry = {
        f.__name__: OpenAIFunction.from_function(f)
        for f in functions
    }
    req = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": question}
        ],
        "functions": [f.to_openai_schema() for f in registry.values()]
    }
    response = openai.ChatCompletion.create(**req)
    if not any([c["finish_reason"] == "function_call"
                for c in response["choices"]]):
        return response

    messages, results = call_functions(response, registry)
    req["messages"].extend(messages)
    return openai.ChatCompletion.create(**req)


def call_functions(response, registry):
    """
    Make the actual functions using the initial responses

    :param response:
    :param registry:
    :return:
    """
    messages = []
    all_results = {}
    for c in response["choices"]:
        if c["finish_reason"] == "function_call":
            msg = c["message"]
            messages.append(msg)

            # find and evaluate the function call
            func_data = msg["function_call"]
            name = func_data["name"]
            f = registry[name]
            args = json.loads(func_data["arguments"])
            result = f(**args)

            messages.append({"role": "function", "name": name, "content": json.dumps(result)})
            all_results[name] = result
    return messages, all_results
