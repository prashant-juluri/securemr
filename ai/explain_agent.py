import json
from pathlib import Path
from config import AI_MODELS
from ai.json_utils import parse_and_validate


PROMPT_PATH = Path(__file__).parent / "prompts/explain_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/explain_schema.json"


class ExplainAgent:

    def __init__(self, llm):

        self.llm = llm

        with open(PROMPT_PATH) as f:
            self.prompt_template = f.read()

        with open(SCHEMA_PATH) as f:
            self.schema = json.load(f)

    def analyze(self, finding):

        prompt = self.prompt_template.format(
            rule=finding.rule,
            severity=finding.severity,
            cwe=finding.cwe,
            owasp=finding.owasp,
            file=finding.file,
            line=finding.line,
            snippet=finding.snippet
        )

        response = self.llm.generate(
            prompt,
            model=AI_MODELS["explain"]
        )

        return parse_and_validate(response, self.schema)