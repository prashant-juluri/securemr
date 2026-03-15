import subprocess
import json
import tempfile
import os


def run_semgrep(target_path="."):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
        output_path = tmp_file.name
        tmp_file.flush()  # Ensure any buffered data is written

    # The temporary file is now closed but still exists on disk

    try:
        cmd = [
        "semgrep",
        "--config=p/default",
        "--config=p/secrets",
        "--config=p/dockerfile",
        "--config=p/supply-chain",
        "--config=p/owasp-top-ten",
        "--config=p/r2c-bug-scan",
        "--config=p/gitleaks",
        "--no-git-ignore",
        "--metrics=off",
        "--timeout=0",
        "--optimizations=all",
        "--json",
        "--output", output_path,
        target_path
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

        return data

    finally:
        # Ensure the temporary file is always deleted
        try:
            os.remove(output_path)
        except OSError:
            pass  # File may have already been deleted or inaccessible