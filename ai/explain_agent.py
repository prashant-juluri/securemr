import json
from pathlib import Path
from string import Template
from config import AI_MODELS
from ai.json_utils import parse_and_validate


PROMPT_PATH = Path(__file__).parent / "prompts/explain_prompt.txt"
SCHEMA_PATH = Path(__file__).parent / "schemas/explain_schema.json"


class ExplainAgent:

    def __init__(self, llm):

        self.llm = llm

        with open(PROMPT_PATH) as f:
            self.prompt_template = Template(f.read())

        with open(SCHEMA_PATH) as f:
            self.schema = json.load(f)


    def analyze(self, finding):

        try:
            prompt = self.prompt_template.safe_substitute(
                rule=finding.rule,
                severity=finding.severity,
                cwe=finding.cwe,
                owasp=finding.owasp,
                file=finding.file,
                line=finding.line,
                snippet=finding.snippet
            )

            print("[SecureMR] Explain prompt generated")

            response = self.llm.generate(
                prompt,
                model=AI_MODELS["explain"]
            )

        except Exception as e:
            print("[SecureMR] ExplainAgent failed to generate response:", str(e))
            raise e


        print("[SecureMR] Explain LLM raw response:", response)

        return parse_and_validate(response, self.schema)