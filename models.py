import hashlib


class Finding:

    def __init__(self, file, line, rule, severity, snippet):

        self.file = file
        self.line = line
        self.rule = rule
        self.severity = severity
        self.snippet = snippet

        self.cwe = None
        self.owasp = None
        self.category = None

        self.risk_weight = None
        self.new_issue = False

        self.fingerprint = self.generate_fingerprint()


    def generate_fingerprint(self):

        base = f"{self.file}:{self.line}:{self.rule}"

        return hashlib.sha256(base.encode()).hexdigest()


    def __repr__(self):

        return f"<Finding {self.rule} {self.file}:{self.line}>"