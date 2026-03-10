import json
from models import Finding


def normalize_severity(severity):

    mapping = {
        "ERROR": "HIGH",
        "WARNING": "MEDIUM",
        "INFO": "LOW"
    }

    return mapping.get(severity, "MEDIUM")


def parse_semgrep(file_path):

    findings = []

    try:
        with open(file_path, "r") as f:

            content = f.read().strip()

            if not content:
                print("Semgrep output is empty.")
                return findings

            data = json.loads(content)

    except FileNotFoundError:
        print(f"Semgrep file not found: {file_path}")
        return findings

    except json.JSONDecodeError:
        print("Invalid JSON in Semgrep output.")
        return findings


    results = data.get("results", [])

    for r in results:

        file = r.get("path")
        rule = r.get("check_id")

        line = r.get("start", {}).get("line", 0)

        raw_severity = r.get("extra", {}).get("severity", "WARNING")

        severity = normalize_severity(raw_severity)

        snippet = r.get("extra", {}).get("lines") or ""

        snippet = snippet.strip()

        finding = Finding(
                    file=file,
                    line=line,
                    rule=rule,
                    severity=severity,
                    snippet=snippet
                        )

        finding.raw = r

        findings.append(finding)

    return findings