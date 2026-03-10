import os
import subprocess


def get_changed_files():
    """
    Determine which files were changed in the current branch / PR / MR.

    Supports:
    - GitHub Actions
    - GitLab CI
    - Local development
    """

    base = None

    # GitHub Actions
    github_base = os.getenv("GITHUB_BASE_REF")
    if github_base:
        base = f"origin/{github_base}"

    # GitLab CI
    gitlab_base = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    if gitlab_base:
        base = f"origin/{gitlab_base}"

    # Local fallback
    if base is None:
        base = "origin/main"

    print(f"[SecureMR] Using diff base: {base}")

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            capture_output=True,
            text=True,
            check=True
        )

        files = result.stdout.strip().split("\n")

        return [normalize_path(f) for f in files if f]

    except subprocess.CalledProcessError:

        print("[SecureMR] Unable to diff against base branch. Falling back to local diff.")

        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True
        )

        files = result.stdout.strip().split("\n")

        return [normalize_path(f) for f in files if f]


def normalize_path(path):
    """
    Normalize file paths so comparisons work reliably.
    """

    return os.path.normpath(path)


def tag_new_findings(findings, changed_files):
    """
    Mark findings that occur in files modified in the current change.
    """

    changed_set = set(normalize_path(f) for f in changed_files)

    for finding in findings:

        file_path = normalize_path(finding.file)

        if file_path in changed_set:
            finding.new_issue = True