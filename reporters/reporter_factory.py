import os

from reporters.console_reporter import ConsoleReporter
from reporters.github_reporter import GitHubReporter
from reporters.gitlab_reporter import GitLabReporter


class ReporterFactory:

    @staticmethod
    def create():

        reporters = []

        reporters.append(ConsoleReporter())

        if os.getenv("GITHUB_TOKEN"):
            reporters.append(GitHubReporter())

        if os.getenv("GITLAB_TOKEN"):
            reporters.append(GitLabReporter())

        return reporters