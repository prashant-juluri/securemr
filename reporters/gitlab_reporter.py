import requests

from reporters.base_reporter import BaseReporter
from reporters.formatter import format_report


class GitlabReporter(BaseReporter):

    def __init__(self, token, project_id, mr_iid, api_url):

        self.token = token
        self.project_id = project_id
        self.mr_iid = mr_iid
        self.api_url = api_url


    def publish(self, report):

        try:

            print(f"[SecureMR] Publishing GitLab report to project {self.project_id}, MR !{self.mr_iid}")

            body = "## 🔒 SecureMR Security Report\n\n"

            for f in report["findings"]:

                review = f.get("review", {})
                explanation = review.get("explanation", {})
                risk = review.get("risk", {})
                fix = review.get("fix", {})

                body += f"### File: `{f['file']}`\n"
                body += f"Rule: `{f['rule']}`\n\n"

                if explanation:
                    body += "**Explanation**\n"
                    body += explanation.get("explanation", "") + "\n\n"

                if risk:
                    body += f"**Risk Level:** {risk.get('risk_level','')}\n"
                    body += risk.get("risk_reason", "") + "\n\n"

                if fix:
                    body += "**Suggested Fix**\n"
                    body += fix.get("fix_description","") + "\n\n"

                    patch = fix.get("patch_diff")

                    if patch:
                        body += "```diff\n"
                        body += patch
                        body += "\n```\n\n"

        except Exception as e:

            print(f"[SecureMR] Error formatting GitLab report: {e}")
            body = "SecureMR failed to format the security report."

        try:

            url = f"{self.api_url}/projects/{self.project_id}/merge_requests/{self.mr_iid}/notes"

            headers = {
                "PRIVATE-TOKEN": self.token,
                "Content-Type": "application/json"
            }

            payload = {
                "body": body
            }

            print("[SecureMR] Posting comment to GitLab MR")

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                print("[SecureMR] Comment posted to GitLab MR")

            else:
                print("[SecureMR] Failed to post GitLab comment:", response.text)

        except Exception as e:

            print("[SecureMR] GitLab API call failed:", str(e))