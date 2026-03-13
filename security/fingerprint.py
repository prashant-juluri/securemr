import hashlib


def normalize_code(text):
    """
    Normalize code snippet so formatting changes
    don't change the fingerprint.
    """

    if not text:
        return ""

    text = text.strip()

    # collapse whitespace
    text = " ".join(text.split())

    return text


def fingerprint_finding(finding):
    """
    Generate a stable fingerprint for a finding.
    """

    snippet = getattr(finding, "snippet", "")

    normalized = normalize_code(snippet)

    raw = f"{finding.rule}:{normalized}"

    return hashlib.sha256(raw.encode()).hexdigest()