import subprocess
import json
import tempfile
import os


def run_semgrep(target_path="."):

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    output_path = tmp_file.name

    cmd = [
    "semgrep",
    "--config=p/security-audit",
    "--no-git-ignore",
    target_path,
    "--json",
    "--output",
    output_path
    ]

    print(f"[SecureMR] Executing Semgrep on {target_path}")

    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"[SecureMR] Failed to execute Semgrep: {e}")
        return {"results": []}

    try:
        with open(output_path) as f:
            data = json.load(f)
    except Exception:
        print("[SecureMR] Failed to parse Semgrep output")
        data = {"results": []}

    try:
        os.remove(output_path)
    except Exception:
        pass

    return data