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
            pr = os.getenv("PR_NUMBER")

            if token and repo and pr:
                reporters.append(GithubReporter(token, repo, pr))

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