from reporters.base_reporter import BaseReporter


class ConsoleReporter(BaseReporter):

    def publish(self, report):

        print("\n🔒 SecureMR Security Report")
        print("================================")

        print(f"Total Findings: {report['total_findings']}")
        print(f"HIGH: {report['high_risk']}")
        print(f"MEDIUM: {report['medium_risk']}")
        print(f"LOW: {report['low_risk']}")

        print("\nFindings:")

        for f in report["findings"]:

            print("--------------------------------")
            print(f"File: {f['file']}")
            print(f"Rule: {f['rule']}")
            print(f"CWE: {f['cwe']}")
            print(f"Risk: {f['risk']}")

        print("================================\n")