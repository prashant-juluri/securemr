import json


def clean_llm_json(response: str) -> str:
    """
    Cleans LLM responses so they can be parsed as JSON.
    Handles markdown code blocks like ```json ... ```
    """

    if not response:
        return response

    response = response.strip()

    # Remove ```json ... ``` blocks
    if response.startswith("```"):
        lines = response.splitlines()

        # Remove first line ```json or ```
        lines = lines[1:]

        # Remove last line ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines)

    response = response.strip()

    # Remove leading 'json'
    if response.lower().startswith("json"):
        response = response[4:].strip()

    return response


def parse_and_validate(response: str, schema: dict):

    try:

        cleaned = clean_llm_json(response)

        data = json.loads(cleaned)

        # Optional minimal schema validation
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