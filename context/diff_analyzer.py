import os
import subprocess


def get_changed_files():
    """
    Determine files changed in the current branch/PR/MR.
    Works across GitHub Actions, GitLab CI, and local environments.
    """

    github_base = os.getenv("GITHUB_BASE_REF")
    gitlab_base = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")

    if github_base:
        base = f"origin/{github_base}"
        print(f"[SecureMR] GitHub PR detected. Diff base: {base}")

    elif gitlab_base:
        base = f"origin/{gitlab_base}"
        print(f"[SecureMR] GitLab MR detected. Diff base: {base}")

    else:
        try:
            base = subprocess.check_output(
                ["git", "merge-base", "HEAD", "origin/main"],
                text=True
            ).strip()

            print(f"[SecureMR] Using merge-base fallback: {base}")

        except Exception:
            base = "HEAD"
            print("[SecureMR] Unable to determine merge-base. Using HEAD.")

    result = subprocess.run(
        ["git", "diff", "--name-only", base],
        capture_output=True,
        text=True
    )

    files = result.stdout.strip().split("\n")

    return [normalize_path(f) for f in files if f]


def normalize_path(path):
    return os.path.normpath(path)


def tag_new_findings(findings, changed_files):

    changed = set(normalize_path(f) for f in changed_files)

    for finding in findings:
        if normalize_path(finding.file) in changed:
            finding.new_issue = True