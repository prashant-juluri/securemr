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
        print("[SecureMR] No PR/MR detected. Diff filtering disabled.")
        return None

    try:


        # Ensure full git history exists (CI often uses shallow clones)
        subprocess.run(["git", "fetch", "--unshallow"], check=False)

        # Ensure base branch exists locally
        subprocess.run(["git", "fetch", "origin", base_branch], check=False)

        merge_base = subprocess.check_output(
            ["git", "merge-base", "HEAD", f"origin/{base_branch}"],
            text=True
        ).strip()

        print(f"[SecureMR] Using merge-base: {merge_base}")

        result = subprocess.run(
            ["git", "diff", "--name-only", merge_base, "HEAD"],
            capture_output=True,
            text=True
        )

        files = result.stdout.strip().split("\n")

        files = [normalize_path(f) for f in files if f]

        print(f"[SecureMR] Files changed in PR/MR: {files}")

        return files

    except Exception as e:

        print("[SecureMR] Diff detection failed:", e)

        return None


def normalize_path(path):
    return os.path.normpath(path)


def tag_new_findings(findings, changed_files):
    """
    Tag findings that are part of the current diff.
    """

    if changed_files is None:
        print("[SecureMR] Running full repository analysis.")
        for finding in findings:
            finding.new_issue = True
        return

    changed = set(normalize_path(f) for f in changed_files)

    for finding in findings:

        normalized = normalize_path(finding.file)

        if normalized in changed:
            finding.new_issue = True
        else:
            finding.new_issue = False