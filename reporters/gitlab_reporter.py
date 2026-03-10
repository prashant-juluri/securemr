import os
import requests

from reporters.base_reporter import BaseReporter


class GitLabReporter(BaseReporter):

    def __init__(self):

        self.token = os.getenv("GITLAB_TOKEN")
        self.project_id = os.getenv("CI_PROJECT_ID")
        self.mr_iid = os.getenv("CI_MERGE_REQUEST_IID")
        self.api_url = os.getenv("CI_API_V4_URL")

    def publish(self, report):

        if not self.token or not self.project_id or not self.mr_iid:
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

        url = f"{self.api_url}/projects/{self.project_id}/merge_requests/{self.mr_iid}/notes"

        headers = {
            "PRIVATE-TOKEN": self.token
        }

        requests.post(url, headers=headers, json={"body": body})