import os
import json
import requests

from reporters.base_reporter import BaseReporter


class GithubReporter(BaseReporter):

    def __init__(self):

        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY")
        self.event_path = os.getenv("GITHUB_EVENT_PATH")

        self.pr_number = self._extract_pr_number()

    def _extract_pr_number(self):

        if not self.event_path:
            return None

        try:
            with open(self.event_path) as f:
                event = json.load(f)

            return (
                event.get("pull_request", {}).get("number")
                or event.get("number")
            )

        except Exception:
            return None

    def publish(self, report):

        if not self.token or not self.repo or not self.pr_number:
            return

        body = (
            "🔒 **SecureMR Security Report**\n\n"
            f"Total Findings: {report['total_findings']}\n"
            f"HIGH: {report['high_risk']}\n"
            f"MEDIUM: {report['medium_risk']}\n"
            f"LOW: {report['low_risk']}\n\n"
            "### Findings\n"
        )

        for f in report["findings"]:

            body += (
                f"- `{f['file']}` — {f['rule']} "
                f"(CWE: {f['cwe']}) — **{f['risk']}**\n"
            )

        url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        requests.post(url, headers=headers, json={"body": body})