from models import Finding
from utils.code_context import get_code_context


def parse_semgrep(data):

    findings = []

    results = data.get("results", [])

    for result in results:

        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})

        file_path = result.get("path")
        rule_id = result.get("check_id")
        message = extra.get("message")
        severity = extra.get("severity")

        line = None
        if result.get("start"):
            line = result["start"].get("line")

        # CWE may not always exist
        cwe = metadata.get("cwe")

        snippet = ""

        extra = result.get("extra", {})

        if "lines" in extra:
            snippet = extra["lines"]
        elif "message" in result:
            snippet = result["message"]

        finding = Finding(
            file_path=file_path,
            rule_id=rule_id,
            message=message,
            severity=severity,
            line=line,
            cwe=cwe,
            snippet=snippet
        )

        print("[SecureMR] Snippet sent to LLM:")
        print(finding.snippet)

        findings.append(finding)
        finding.context = get_code_context(finding.file_path, finding.line)

    return findings