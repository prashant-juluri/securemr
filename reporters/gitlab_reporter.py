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