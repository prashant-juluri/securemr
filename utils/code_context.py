def get_code_context(file_path, line, radius=6):

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        start = max(line - radius - 1, 0)
        end = min(line + radius, len(lines))

        snippet = "".join(lines[start:end])

        return snippet

    except Exception as e:
        print(f"[SecureMR] Failed to extract code context: {e}")
        return ""