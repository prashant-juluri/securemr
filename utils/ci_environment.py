import os


class CIEnvironment:

    @staticmethod
    def detect():

        # GitHub Actions
        if os.getenv("GITHUB_ACTIONS"):
            return "github"

        # GitLab CI
        if os.getenv("GITLAB_CI"):
            return "gitlab"

        # Generic CI (Jenkins, CircleCI etc.)
        if os.getenv("CI"):
            return "ci"

        # Local execution
        return "local"