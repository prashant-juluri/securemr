import os

from reporters.github_reporter import GithubReporter
from reporters.gitlab_reporter import GitlabReporter
from reporters.console_reporter import ConsoleReporter


class ReporterFactory:

    @staticmethod
    def create():

        # GitHub detection
        if os.getenv("GITHUB_ACTIONS") == "true":

            token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPOSITORY")
            pr = os.getenv("PR_NUMBER")

            if token and repo and pr:
                print("[SecureMR] GitHub PR reporter enabled")
                return GithubReporter(token, repo, pr)

        # GitLab detection
        if os.getenv("GITLAB_CI") == "true":

            token = os.getenv("GITLAB_TOKEN")
            project_id = os.getenv("CI_PROJECT_ID")
            mr_iid = os.getenv("CI_MERGE_REQUEST_IID")
            api_url = os.getenv("CI_API_V4_URL")

            if token and project_id and mr_iid:
                print("[SecureMR] GitLab MR reporter enabled")
                return GitlabReporter(token, project_id, mr_iid, api_url)

        print("[SecureMR] Using console reporter")
        return ConsoleReporter()