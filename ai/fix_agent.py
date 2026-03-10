import json
from pathlib import Path

from config import AI_MODELS
from ai.json_utils import parse_and_validate


PROMPT_PATH = Path(__file__).parent / "prompts/fix_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/fix_schema.json"


class FixAgent:

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

    def analyze(self, finding):

        prompt = self.prompt_template.format(
            rule=finding.rule,
            cwe=finding.cwe,
            file=finding.file,
            line=finding.line,
            snippet=finding.snippet
        )

        response = self.llm.generate(
            prompt,
            model=AI_MODELS["fix"]
        )

        return parse_and_validate(response, self.schema)