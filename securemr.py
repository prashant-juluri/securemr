from scanners.semgrep_parser import parse_semgrep
from context.diff_analyzer import get_changed_files, tag_new_findings
from knowledge.vulnerability_db import enrich_findings
from knowledge.risk_scoring import compute_risk_score


def main():

    findings = parse_semgrep("sample_findings/semgrep.json")

    changed = get_changed_files()

    tag_new_findings(findings, changed)

    enrich_findings(findings)

    for f in findings:

        score = compute_risk_score(f)

        print(
            f.file,
            f.rule,
            f.cwe,
            f.owasp,
            f"score={score}",
            f"new={f.new_issue}"
        )


if __name__ == "__main__":
    main()