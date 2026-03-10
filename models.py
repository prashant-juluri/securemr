class Finding:

    def __init__(self, file, line, rule, severity, snippet):

        self.file = file
        self.line = line
        self.rule = rule
        self.severity = severity
        self.snippet = snippet

        self.cwe = None
        self.owasp = None
        self.new_issue = False

    def __repr__(self):

        return f"<Finding {self.rule} {self.file}:{self.line}>"