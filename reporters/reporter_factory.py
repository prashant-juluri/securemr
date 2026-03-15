import os

from utils.ci_environment import CIEnvironment
from reporters.github_reporter import GithubReporter
from reporters.gitlab_reporter import GitlabReporter
from reporters.console_reporter import ConsoleReporter


class ReporterFactory:

    @staticmethod
    def create():

        reporters = []

        environment = CIEnvironment.detect()

        print(f"[SecureMR] Environment detected: {environment}")

        # GitHub
        if environment == "github":

            token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPOSITORY")

            import json
            event_path = os.getenv("GITHUB_EVENT_PATH")

            pr = None

            if event_path and os.path.exists(event_path):

                with open(event_path) as f:
                    event = json.load(f)

                if "pull_request" in event:
                    pr = event["pull_request"]["number"]

            if token and repo and pr:
                print(f"[SecureMR] GitHub env check:")
                print(f"  token present: {bool(token)}")
                print(f"  repo: {repo}")
                print(f"  pr: {pr}")

                reporters.append(GithubReporter(token, repo, pr))
                print(f"[SecureMR] GitHub reporter initialized for repo {repo} and PR #{pr}")

        # GitLab
        if environment == "gitlab":

            token = os.getenv("GITLAB_TOKEN")
            project_id = os.getenv("CI_PROJECT_ID")
            mr_iid = os.getenv("CI_MERGE_REQUEST_IID")
            api_url = os.getenv("CI_API_V4_URL")

            if token and project_id and mr_iid:
                reporters.append(GitlabReporter(token, project_id, mr_iid, api_url))

        # Always include console output
        reporters.append(ConsoleReporter())

        return reporters