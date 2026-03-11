import requests


class GitlabReporter:

    def __init__(self, token, project_id, mr_iid, api_url):

        self.token = token
        self.project_id = project_id
        self.mr_iid = mr_iid
        self.api_url = api_url


    def publish(self, report):

        if not self.mr_iid:
            print("[SecureMR] No merge request detected. Skipping GitLab comment.")
            return

        url = f"{self.api_url}/projects/{self.project_id}/merge_requests/{self.mr_iid}/notes"

        headers = {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json"
        }

        payload = {
            "body": report
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 201:
                print("[SecureMR] Comment posted to GitLab MR")

            else:
                print(
                    "[SecureMR] Failed to post GitLab comment:",
                    response.status_code,
                    response.text
                )

        except requests.exceptions.RequestException as e:
            print("[SecureMR] GitLab API request failed:", str(e))