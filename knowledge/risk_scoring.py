SEVERITY_BASE = {
    "HIGH": 7,
    "MEDIUM": 5,
    "LOW": 3
}


def compute_risk_score(finding):

    base = SEVERITY_BASE.get(finding.severity, 5)

    vulnerability_weight = finding.risk_weight or 0

    score = base + vulnerability_weight

    if finding.new_issue:
        score += 2

    return min(score, 10)