class Finding:

    def __init__(
        self,
        file_path,
        rule_id,
        message,
        severity,
        line,
        cwe=None
    ):

        # Core semgrep fields
        self.file_path = file_path
        self.rule_id = rule_id
        self.rule = rule_id  # backward compatibility

        self.message = message
        self.severity = severity
        self.line = line
        self.cwe = cwe

        # SecureMR metadata
        self.new = False
        self.risk_score = None


    def to_dict(self):
        return {
            "file_path": self.file_path,
            "rule_id": self.rule_id,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
            "line": self.line,
            "cwe": self.cwe,
            "new": self.new,
            "risk_score": self.risk_score
        }


    def __repr__(self):
        return (
            f"Finding(file={self.file_path}, "
            f"rule={self.rule_id}, "
            f"severity={self.severity}, "
            f"line={self.line}, "
            f"cwe={self.cwe})"
        )