# Functools for OpenAI GPT Functions

OpenAI just released GPT Functions: https://openai.com/blog/function-calling-and-other-api-updates

But it's really cumbersome to make the actual function signature.
And manually parse results and chain the calls:

```shell
curl https://api.openai.com/v1/chat/completions -u :$OPENAI_API_KEY -H 'Content-Type: application/json' -d '{
  "model": "gpt-3.5-turbo-0613",
  "messages": [
    {"role": "user", "content": "What is the weather like in Boston?"}
  ],
  "functions": [
    {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"]
          }
        },
        "required": ["location"]
      }
    }
  ]
}'
```

## Use aifunctools instead

Instead, aifunctools automatically parses available python type annotations 
and docstrings so you don't have to do all of the manual work:

```python
from aifunctools.openai_funcs import complete_with_functions

def get_current_weather(location: str, unit: str) -> dict:
    """
    Get the current weather in a given location

    :param location: The city and state, e.g. San Francisco, CA
    :param unit: Either "celsius" or "fahrenheit"
    :return: the current temperature, unit, and a description
    """
    return {"temperature": 22, "unit": "celsius", "description": "Sunny"}


resp = complete_with_functions("What is the weather like in Boston?",
                               get_current_weather)
# The response should contain: "The weather in Boston is currently sunny with a temperature of 22 degrees Celsius."
```

## What's next

### OpenAPI Specs

Python functions are great, but what would really be great is to parse openapi specs from remote services.
Imagine where every service provider makes their api spec available and agents can just
crawl these APIs and use aifunctools to chain them together.

### Richer types

For this hack we only support the basic string / number / boolean types.
By making this more flexible we can get much richer behavior.

### Error handling

I'm sure there are lots of cases where incomplete docstrings and type signatures
will cause errors. We can make these more robust (or use some reasonable defaults).