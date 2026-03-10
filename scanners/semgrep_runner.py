import subprocess
import json
import tempfile
import os


def run_semgrep():

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    output_path = tmp_file.name

    cmd = [
        "semgrep",
        "--config=p/security-audit",
        "--json",
        "--output",
        output_path
    ]

    subprocess.run(cmd, check=True)

    with open(output_path) as f:
        data = json.load(f)

    os.remove(output_path)

    return data