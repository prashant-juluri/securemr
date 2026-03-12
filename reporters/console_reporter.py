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

            review = f.get("review") or {}

            explanation = review.get("explanation") or {}
            risk = review.get("risk") or {}
            fix = review.get("fix") or {}

            # Explanation
            if isinstance(explanation, dict) and "explanation" in explanation:
                print("\nExplanation:")
                print(explanation["explanation"])

            # Risk
            if isinstance(risk, dict) and "risk_level" in risk:
                print(f"\nRisk Level: {risk.get('risk_level', '')}")
                print(f"Risk Reason: {risk.get('risk_reason', '')}")

            # Fix
            if isinstance(fix, dict) and "fix_description" in fix:
                print("\nSuggested Fix:")
                print(fix["fix_description"])

            # Debug fallback if parsing failed
            if "error" in explanation or "error" in risk or "error" in fix:
                print("\n⚠ AI Output Parsing Issue")
                print("Raw AI response detected.")

        print("================================\n")