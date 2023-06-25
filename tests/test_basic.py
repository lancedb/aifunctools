from aifunctools.openai_funcs import complete_with_functions


def get_current_weather(location: str, unit: str, foo: int=None, bar: list[bool]=None) -> dict:
    """
    This is a short description

    This is a long description

    :param location: The city and state, e.g. San Francisco, CA
    :param unit: Either "celsius" or "fahrenheit"
    :return: the current temperature, unit, and a description
    """
    return {"temperature": 22, "unit": "celsius", "description": "Sunny"}


def test_basic():
    resp = complete_with_functions("What is the weather like in Boston?",
                                   get_current_weather)
    c = resp["choices"][0]
    assert c["finish_reason"] == "stop"
    content = c["message"]["content"]
    assert "22 degrees Celsius" in content
    assert "weather" in content
    assert "Boston" in content
