import os
import subprocess


def get_changed_files():
    """
    Determine files changed in the current branch/PR/MR.
    Works across GitHub Actions, GitLab CI, and local environments.
    """

    github_base = os.getenv("GITHUB_BASE_REF")
    gitlab_base = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")

    base_branch = None

    if github_base:
        base_branch = github_base
        print(f"[SecureMR] GitHub PR detected. Base branch: {base_branch}")

    elif gitlab_base:
        base_branch = gitlab_base
        print(f"[SecureMR] GitLab MR detected. Base branch: {base_branch}")

    else:
        base_branch = "main"
        print(f"[SecureMR] Local run detected. Defaulting base branch to: {base_branch}")

    try:
        # Ensure base branch exists locally
        subprocess.run(
            ["git", "fetch", "origin", base_branch],
            capture_output=True,
            text=True
        )

        merge_base = subprocess.check_output(
            ["git", "merge-base", "HEAD", f"origin/{base_branch}"],
            text=True
        ).strip()

        print(f"[SecureMR] Using merge-base: {merge_base}")

    except Exception as e:

        print("[SecureMR] Failed to determine merge-base:", e)
        merge_base = "HEAD"

    result = subprocess.run(
        ["git", "diff", "--name-only", merge_base, "HEAD"],
        capture_output=True,
        text=True
    )

    files = result.stdout.strip().split("\n")

    files = [normalize_path(f) for f in files if f]

    print(f"[SecureMR] Files changed in PR/MR: {files}")

    return files


def normalize_path(path):
    return os.path.normpath(path)


def tag_new_findings(findings, changed_files):

    changed = set(normalize_path(f) for f in changed_files)

    for finding in findings:

        normalized = normalize_path(finding.file)

        if normalized in changed:
            finding.new_issue = True
        else:
            finding.new_issue = False