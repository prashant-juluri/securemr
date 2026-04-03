import json
import re
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


    def _decode_jsonish_value(self, value):

        return (
            value.replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace('\\"', '"')
                .replace("\\\\", "\\")
        )


    def _extract_json_string_field(self, text, field_name):

        marker = f'"{field_name}"'
        start = text.find(marker)

        if start == -1:
            return ""

        colon = text.find(":", start + len(marker))

        if colon == -1:
            return ""

        index = colon + 1

        while index < len(text) and text[index].isspace():
            index += 1

        if index >= len(text) or text[index] != '"':
            return ""

        index += 1
        chars = []
        escaped = False

        while index < len(text):
            char = text[index]

            if escaped:
                chars.append("\\" + char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                break
            else:
                chars.append(char)

            index += 1

        if escaped:
            chars.append("\\")

        return self._decode_jsonish_value("".join(chars)).strip()


    def _extract_markdown_block(self, text, language):

        pattern = rf"```{language}\s*(.*?)```"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if not match:
            return ""

        return match.group(1).strip()


    def _extract_generic_code_block(self, text):

        matches = re.findall(r"```([a-zA-Z0-9_-]*)\s*(.*?)```", text, re.DOTALL)

        for language, content in matches:
            if language.lower() != "diff":
                return content.strip()

        return ""


    def _extract_diff_lines(self, text):

        lines = text.splitlines()
        diff_lines = []
        collecting = False

        for line in lines:
            if line.startswith(("+", "-", "@@")):
                diff_lines.append(line)
                collecting = True
            elif collecting and line.strip():
                break

        return "\n".join(diff_lines).strip()


    def _split_embedded_fix_sections(self, fix_description):

        if not fix_description:
            return "", "", ""

        section_pattern = (
            r"(?is)\b(?:here(?:'s| is)\s+)?"
            r"(secure\s+code\s+example|patched\s+code|code\s+example)\s*:?\s*(python)?\s*"
        )
        section_match = re.search(section_pattern, fix_description)

        if not section_match:
            return fix_description.strip(), "", ""

        description = fix_description[:section_match.start()].strip().rstrip(":")
        remainder = fix_description[section_match.end():].strip()

        diff_pattern = r"(?is)\b(?:patch\s+diff|diff)\s*:?\s*"
        diff_match = re.search(diff_pattern, remainder)

        if diff_match:
            secure_code_example = remainder[:diff_match.start()].strip()
            patch_diff = remainder[diff_match.end():].strip()
        else:
            secure_code_example = remainder.strip()
            patch_diff = ""

        description = re.sub(r"(?is)\bhere(?:'s| is)\s+the\s*$", "", description).strip()

        return description, secure_code_example, patch_diff


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

        fix_description = self._extract_json_string_field(fallback_text, "fix_description")
        secure_code_example = self._extract_json_string_field(fallback_text, "secure_code_example")
        patch_diff = self._extract_json_string_field(fallback_text, "patch_diff")

        if not secure_code_example:
            secure_code_example = self._extract_markdown_block(raw_response, "python")

        if not patch_diff:
            patch_diff = self._extract_markdown_block(raw_response, "diff")

        if not patch_diff:
            patch_diff = self._extract_diff_lines(raw_response)

        if not secure_code_example:
            secure_code_example = self._extract_generic_code_block(raw_response)

        if not fix_description:
            text_without_blocks = re.sub(r"```.*?```", "", raw_response, flags=re.DOTALL).strip()
            fix_description = clean_llm_json(text_without_blocks).strip() or fallback_text

        embedded_description, embedded_code, embedded_diff = self._split_embedded_fix_sections(
            fix_description
        )

        if embedded_description:
            fix_description = embedded_description

        if not secure_code_example and embedded_code:
            secure_code_example = embedded_code

        if not patch_diff and embedded_diff:
            patch_diff = embedded_diff

        print("[SecureMR] FixAgent salvaging malformed fix response")

        return {
            "fix_description": fix_description,
            "secure_code_example": secure_code_example,
            "patch_diff": patch_diff
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
