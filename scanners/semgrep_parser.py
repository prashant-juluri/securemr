from models import Finding


def parse_semgrep(data):

    findings = []

    results = data.get("results", [])

    for r in results:

        rule = r.get("check_id", "")
        path = r.get("path", "")

        start = r.get("start", {})
        line = start.get("line", 0)

        extra = r.get("extra", {})
        severity = extra.get("severity", "")

        metadata = extra.get("metadata", {})

        cwe = ""
        if "cwe" in metadata:
            cwe_data = metadata["cwe"]
            if isinstance(cwe_data, list) and len(cwe_data) > 0:
                cwe = cwe_data[0]

        finding = Finding(
            file=path,
            line=line,
            rule=rule,
            severity=severity,
            cwe=cwe
        )

        findings.append(finding)

    return findings