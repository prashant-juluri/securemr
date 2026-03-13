import json
import os

from security.fingerprint import fingerprint_finding


BASELINE_FILE = ".securemr_baseline.json"


def load_baseline():

    if not os.path.exists(BASELINE_FILE):
        return set()

    with open(BASELINE_FILE) as f:
        data = json.load(f)

    return set(data)


def save_baseline(findings):

    fingerprints = [
        fingerprint_finding(f)
        for f in findings
    ]

    with open(BASELINE_FILE, "w") as f:
        json.dump(fingerprints, f, indent=2)


def mark_new_findings(findings):

    baseline = load_baseline()

    new_findings = []

    for finding in findings:

        fp = fingerprint_finding(finding)

        if fp not in baseline:
            finding.new_issue = True
            new_findings.append(finding)
        else:
            finding.new_issue = False

    return new_findings