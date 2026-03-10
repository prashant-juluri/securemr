import json
from pathlib import Path

from config import AI_MODELS
from ai.json_utils import parse_and_validate


PROMPT_PATH = Path(__file__).parent / "prompts/risk_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/risk_schema.json"


class RiskAgent:

    def __init__(self, llm):

        self.llm = llm
        self.prompt_template = self._load_prompt()
        self.schema = self._load_schema()

    def _load_prompt(self):

        with open(PROMPT_PATH) as f:
            return f.read()

    def _load_schema(self):

        with open(SCHEMA_PATH) as f:
            return json.load(f)

    def analyze(self, finding, explanation):

        prompt = self.prompt_template.format(
            rule=finding.rule,
            severity=finding.severity,
            cwe=finding.cwe,
            owasp=finding.owasp,
            new_issue=finding.new_issue,
            explanation=explanation
        )

        response = self.llm.generate(
            prompt,
            model=AI_MODELS["risk"]
        )

        return parse_and_validate(response, self.schema)