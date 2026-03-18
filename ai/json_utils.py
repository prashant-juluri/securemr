import json
from typing import Any


def clean_llm_json(response: Any) -> str:
    """
    Cleans LLM responses so they can be parsed as JSON.
    Handles markdown code blocks like ```json ... ```
    """

    if response is None:
        return ""

    if not isinstance(response, str):
        print(f"[SecureMR] Unexpected LLM response type for cleaning: {type(response).__name__}")
        return str(response)

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


def _extract_json_object(response: str):
    start = response.find("{")

    while start != -1:
        depth = 0

        for index in range(start, len(response)):
            char = response[index]

            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1

                if depth == 0:
                    candidate = response[start:index + 1]

                    try:
                        return json.loads(candidate)
                    except Exception:
                        break

        start = response.find("{", start + 1)

    return None


def safe_parse(response: Any):

    try:
        if isinstance(response, dict):
            return response

        if response is None:
            print("[SecureMR] LLM response was None")
            return {
                "error": "invalid_json",
                "raw_response": response
            }

        if not isinstance(response, str):
            print(f"[SecureMR] Unexpected LLM response type: {type(response).__name__}")
            return {
                "error": "invalid_json",
                "raw_response": str(response)
            }

        cleaned = clean_llm_json(response)

        try:
            return json.loads(cleaned)
        except Exception:
            extracted = _extract_json_object(cleaned)

            if extracted is not None:
                return extracted

            return {
                "error": "invalid_json",
                "raw_response": response
            }

    except Exception as exc:
        print(f"[SecureMR] safe_parse failed non-fatally: {exc}")
        return {
            "error": "invalid_json",
            "raw_response": str(response)
        }


def parse_and_validate(response: Any, schema: dict):

    data = safe_parse(response)

    # Schema validation should NOT break the pipeline
    if schema and isinstance(data, dict):
        required = schema.get("required", [])
        missing = [field for field in required if field not in data]

        if missing:
            print("[SecureMR] Schema mismatch (non-fatal):", missing)

    return data
