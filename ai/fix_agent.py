import json
import traceback
from pathlib import Path
from string import Template

from config import AI_MODELS
from ai.json_utils import clean_llm_json, parse_and_validate, safe_parse


PROMPT_PATH = Path(__file__).parent / "prompts/fix_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/fix_schema.json"


class FixAgent:

    MAX_TOKENS = 800

    def __init__(self, llm):

        self.llm = llm

        with open(PROMPT_PATH) as f:
            self.prompt_template = Template(f.read())

        with open(SCHEMA_PATH) as f:
            self.schema = json.load(f)


    def _fallback_fix_response(self, parsed_response):

        if not isinstance(parsed_response, dict):
            return None

        raw_response = parsed_response.get("raw_response")

        if not raw_response:
            return None

        if not isinstance(raw_response, str):
            raw_response = str(raw_response)

        fallback_text = clean_llm_json(raw_response).strip()

        if not fallback_text:
            return None

        print("[SecureMR] FixAgent falling back to raw text fix description")

        return {
            "fix_description": fallback_text,
            "secure_code_example": "",
            "patch_diff": ""
        }


    def analyze(self, finding, explanation):

        try:

            prompt = self.prompt_template.safe_substitute(
                rule=finding.rule,
                severity=finding.severity,
                cwe=finding.cwe,
                owasp=finding.owasp,
                file=finding.file,
                line=finding.line,
                snippet=finding.snippet,
                explanation=explanation,
                context=finding.context
            )

            print("[SecureMR] Fix prompt generated")

            response = self.llm.generate(
                prompt,
                model=AI_MODELS["fix"],
                response_schema=self.schema,
                max_tokens=self.MAX_TOKENS
            )

            #print("[SecureMR] Fix LLM raw response:", response)
            if isinstance(response, dict):
                parsed = response
            else:
                parsed = safe_parse(response)

            result = parse_and_validate(parsed, self.schema)

            if isinstance(result, dict) and result.get("error") == "invalid_json":
                fallback = self._fallback_fix_response(result)

                if fallback is not None:
                    return fallback

            return result

        except Exception as e:

            print("[SecureMR] FixAgent failed:", str(e))
            traceback.print_exc()

            raise
