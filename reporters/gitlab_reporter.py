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

        body = format_report(report)

        url = f"{self.api_url}/projects/{self.project_id}/merge_requests/{self.mr_iid}/notes"

        headers = {
            "PRIVATE-TOKEN": self.token
        }

        payload = {
            "body": body
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        if response.status_code == 201:
            print("[SecureMR] Comment posted to GitLab MR")
        else:
            print("[SecureMR] Failed to post GitLab comment:", response.text)