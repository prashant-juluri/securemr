import os
import subprocess


REPO_PATH = "/target"


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def git(cmd):
    return run(["git", "-C", REPO_PATH] + cmd)


def normalize_path(path):
    return os.path.normpath(path)


def get_changed_files():
    """
    Determine files changed in PR/MR using CI commit ranges.
    """
    print("[SecureMR] Determining changed files from git diff")
    # ----------------------------
    # GitLab Merge Request pipeline
    # ----------------------------
    gitlab_base = os.getenv("CI_MERGE_REQUEST_DIFF_BASE_SHA")
    gitlab_head = os.getenv("CI_COMMIT_SHA")

    if gitlab_base and gitlab_head:

        print("[SecureMR] GitLab MR detected")
        print(f"[SecureMR] Base SHA: {gitlab_base}")
        print(f"[SecureMR] Head SHA: {gitlab_head}")

        diff = git([
            "diff",
            "--name-only",
            gitlab_base,
            gitlab_head
        ])

        files = diff.splitlines()
        files = [normalize_path(f) for f in files if f]

        print(f"[SecureMR] Files changed in MR: {files}")

        return files

    # ----------------------------
    # GitHub Pull Request pipeline
    # ----------------------------
    try:
        print(f"[SecureMR] Fetching GitHub event path keys")
        github_event = os.getenv("GITHUB_EVENT_PATH")
        #print(f"[SecureMR] GitHub event path keys: {github_event.keys() if github_event else 'N/A'}")
    except Exception as e:
        print(f"[SecureMR] Error accessing GitHub event path: {e}")


    if github_event:

        try:

            import json

            with open(github_event) as f:
                event = json.load(f)

            print(f"[SecureMR] GitHub event loaded: {event.keys()}")

            if "pull_request" in event:

                github_base = event["pull_request"]["base"]["sha"]
                github_head = event["pull_request"]["head"]["sha"]

                print("[SecureMR] GitHub PR detected")
                print(f"[SecureMR] Base SHA: {github_base}")
                print(f"[SecureMR] Head SHA: {github_head}")

                diff = git([
                    "diff",
                    "--name-only",
                    github_base
                ])

                files = diff.splitlines()
                files = [normalize_path(f) for f in files if f]

                print(f"[SecureMR] Files changed in PR: {files}")

                return files

        except Exception as e:

            print(f"[SecureMR] Failed to parse GitHub event: {e}")

    # ----------------------------
    # Local execution fallback
    # ----------------------------
    print("[SecureMR] Local run detected. Attempting merge-base with main.")

    try:

        git(["fetch", "origin", "main"])

        merge_base = git([
            "merge-base",
            "HEAD",
            "origin/main"
        ])

        if not merge_base:

            print("[SecureMR] Merge-base not found. Running full scan.")
            return None

        print(f"[SecureMR] Using merge-base fallback: {merge_base}")

        diff = git([
            "diff",
            "--name-only",
            merge_base,
            "HEAD"
        ])

        files = diff.splitlines()
        files = [normalize_path(f) for f in files if f]

        print(f"[SecureMR] Files changed locally: {files}")

        return files

    except Exception:

        print("[SecureMR] Diff detection failed. Running full scan.")
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

    print(f"[SecureMR] Files considered for new findings: {changed}")

    for finding in findings:

        normalized = normalize_path(finding.file)

        # convert absolute container path → repo relative path
        if normalized.startswith("/target/"):
            normalized = normalized.replace("/target/", "", 1)

        if normalized in changed:
            finding.new_issue = True
        else:
            finding.new_issue = False