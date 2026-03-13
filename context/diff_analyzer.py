import os
import subprocess


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def normalize_path(path):
    return os.path.normpath(path)


def get_changed_files():
    """
    Determine files changed in the current PR/MR.

    Priority order:
    1. GitLab MR pipelines (CI_MERGE_REQUEST_DIFF_BASE_SHA)
    2. GitHub PR pipelines (GITHUB_BASE_REF)
    3. Local fallback using merge-base
    """

    # ----------------------------
    # GitLab Merge Request pipeline
    # ----------------------------
    gitlab_base_sha = os.getenv("CI_MERGE_REQUEST_DIFF_BASE_SHA")

    if gitlab_base_sha:

        print(f"[SecureMR] GitLab MR detected. Diff base SHA: {gitlab_base_sha}")

        diff = run([
            "git",
            "diff",
            "--name-only",
            gitlab_base_sha,
            "HEAD"
        ])

        files = diff.splitlines()

        files = [normalize_path(f) for f in files if f]

        print(f"[SecureMR] Files changed in PR/MR: {files}")

        return files

    # ----------------------------
    # GitHub Pull Request pipeline
    # ----------------------------
    github_base = os.getenv("GITHUB_BASE_REF")

    if github_base:

        print(f"[SecureMR] GitHub PR detected. Base branch: {github_base}")

        subprocess.run(["git", "fetch", "origin", github_base], check=False)

        merge_base = run([
            "git",
            "merge-base",
            "HEAD",
            f"origin/{github_base}"
        ])

        print(f"[SecureMR] Using merge-base: {merge_base}")

        diff = run([
            "git",
            "diff",
            "--name-only",
            merge_base,
            "HEAD"
        ])

        files = diff.splitlines()

        files = [normalize_path(f) for f in files if f]

        print(f"[SecureMR] Files changed in PR/MR: {files}")

        return files

    # ----------------------------
    # Local / fallback execution
    # ----------------------------
    print("[SecureMR] No PR/MR detected. Diff filtering disabled.")

    return None


def tag_new_findings(findings, changed_files):
    """
    Tag findings that belong to files changed in the diff.
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