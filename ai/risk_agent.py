import json
from pathlib import Path
from string import Template

from config import AI_MODELS
from ai.json_utils import parse_and_validate


PROMPT_PATH = Path(__file__).parent / "prompts/risk_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/risk_schema.json"


class RiskAgent:

    def __init__(self, llm):

        self.llm = llm

        with open(PROMPT_PATH) as f:
            self.prompt_template = Template(f.read())

        with open(SCHEMA_PATH) as f:
            self.schema = json.load(f)


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
                explanation=explanation
            )

            print("[SecureMR] Risk prompt generated")

            response = self.llm.generate(
                prompt,
                model=AI_MODELS["risk"]
            )

        except Exception as e:
            print("[SecureMR] RiskAgent failed to generate response:", str(e))
            raise e


        print("[SecureMR] Risk LLM raw response:", response)

        return parse_and_validate(response, self.schema)