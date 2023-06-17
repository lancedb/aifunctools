from aifunctools.openai_funcs import complete_with_functions

def get_current_weather(location: str, unit: str) -> dict:
    """
    Get the current weather in a given location

    :param location: The city and state, e.g. San Francisco, CA
    :param unit: Either "celsius" or "fahrenheit"
    :return: the current temperature, unit, and a description
    """
    return {"temperature": 22, "unit": "celsius", "description": "Sunny"}


def test_basic():
    resp = complete_with_functions("What is the weather like in Boston?",
                                   get_current_weather)
    expected = "The weather in Boston is currently sunny with a temperature of 22 degrees Celsius."
    c = resp["choices"][0]
    assert c["finish_reason"] == "stop"
    assert c["message"]["content"] == expected




