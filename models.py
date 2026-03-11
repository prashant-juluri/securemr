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

        # Canonical fields
        self.file_path = file_path
        self.rule_id = rule_id
        self.message = message
        self.severity = severity
        self.line = line
        self.cwe = cwe

        # Backwards compatibility aliases
        self.file = file_path
        self.rule = rule_id

        # SecureMR metadata
        self.new = False
        self.new_issue = False
        self.risk_score = None


    def to_dict(self):
        return {
            "file_path": self.file_path,
            "file": self.file,
            "rule_id": self.rule_id,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
            "line": self.line,
            "cwe": self.cwe,
            "new": self.new,
            "new_issue": self.new_issue,
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