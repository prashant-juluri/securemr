import os
import requests

from reporters.base_reporter import BaseReporter
from reporters.formatter import format_report


class GithubReporter(BaseReporter):

    def __init__(self):

        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY")
        self.pr_number = os.getenv("PR_NUMBER")

        self.api_url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"


    def publish(self, report):

        body = format_report(report)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        payload = {
            "body": body
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload
        )

        if response.status_code == 201:
            print("[SecureMR] Comment posted to GitHub PR")
        else:
            print("[SecureMR] Failed to post GitHub comment:", response.text)