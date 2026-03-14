import requests

from reporters.base_reporter import BaseReporter


class GithubReporter(BaseReporter):

    def __init__(self, token, repo, pr_number):

        self.token = token
        self.repo = repo
        self.pr_number = pr_number

    def publish(self, report):

        if not self.pr_number:
            print("[SecureMR] No PR number detected. Skipping GitHub comment.")
            return

        try:

            print(f"[SecureMR] Publishing GitHub report to PR #{self.pr_number}")

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
                    body += fix.get("fix_description", "") + "\n\n"

                    patch = fix.get("patch_diff")

                    if patch:
                        body += "```diff\n"
                        body += patch
                        body += "\n```\n\n"

        except Exception as e:

            print("[SecureMR] Error formatting GitHub report:", str(e))
            body = "SecureMR failed to format the security report."

        try:

            url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json"
            }

            payload = {
                "body": body
            }

            print("[SecureMR] Posting comment to GitHub PR")

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                print("[SecureMR] Comment posted to GitHub PR")

            else:
                print("[SecureMR] Failed to post GitHub comment:", response.text)

        except Exception as e:

            print("[SecureMR] GitHub API call failed:", str(e))