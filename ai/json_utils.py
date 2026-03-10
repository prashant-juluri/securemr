import json
from jsonschema import validate, ValidationError


def parse_and_validate(response, schema):

    try:

        data = json.loads(response)

        validate(instance=data, schema=schema)

        return data

    except (json.JSONDecodeError, ValidationError):

        return {
            "error": "invalid_ai_output",
            "raw_response": response
        }