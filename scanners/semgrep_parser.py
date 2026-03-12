from models import Finding


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

        findings.append(finding)

    return findings