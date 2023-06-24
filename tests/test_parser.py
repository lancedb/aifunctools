from aifunctools.parser import parse_function, OpenAIFunction


def get_current_weather(location: str, unit: str, foo: int=None, bar: list[bool]=None) -> dict:
    """
    This is a short description

    This is a long description

    :param location: The city and state, e.g. San Francisco, CA
    :param unit: Either "celsius" or "fahrenheit"
    :return: the current temperature, unit, and a description
    """
    return {"temperature": 22, "unit": "celsius", "description": "Sunny"}


EXPECTED_SCHEMA = {
        "name": "get_current_weather",
        "description": "This is a short description\n\nThis is a long description",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "description": "Either \"celsius\" or \"fahrenheit\""
                },
                "foo": {
                    "type": "integer",
                    "description": "",
                    "default": None
                },
                "bar": {
                    "type": "array",
                    "default": None,
                    "items": {
                        "type": "boolean"
                    },
                    "description": ""
                }
            },
            "required": ["location", "unit"]
        }
    }


def test_parse_function():
    descriptor, validated = parse_function(get_current_weather)
    assert get_current_weather("Boston", "celsius", 1, [True, False]) == validated("Boston", "celsius", 1, [True, False])
    assert descriptor == EXPECTED_SCHEMA


def test_model():
    func = OpenAIFunction.from_function(get_current_weather)
    schema = func.to_openai_schema()
    assert schema == EXPECTED_SCHEMA
