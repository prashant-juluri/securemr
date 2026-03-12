import json


def clean_llm_json(response: str) -> str:
    """
    Cleans LLM responses so they can be parsed as JSON.
    Handles:
    - ```json code blocks
    - leading 'json'
    - stray whitespace
    """

    if not response:
        return response

    response = response.strip()

    # Handle ```json ... ```
    if response.startswith("```"):
        parts = response.split("```")
        if len(parts) >= 2:
            response = parts[1]

    response = response.strip()

    # Remove leading "json"
    if response.startswith("json"):
        response = response[4:].strip()

    return response


def parse_and_validate(response: str, schema: dict):

    try:

        cleaned = clean_llm_json(response)

        data = json.loads(cleaned)

        # Optional schema validation
        if schema:

            required = schema.get("required", [])

            for field in required:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")

        return data

    except Exception:

        return {
            "error": "invalid_ai_output",
            "raw_response": response
        }