def format_report(report):

    lines = []

    lines.append("## 🔒 SecureMR Security Report\n")

    lines.append(f"**Total Findings:** {report['total_findings']}")
    lines.append(f"🔴 **High:** {report['high_risk']}")
    lines.append(f"🟡 **Medium:** {report['medium_risk']}")
    lines.append(f"🟢 **Low:** {report['low_risk']}\n")

    for finding in report["findings"]:

        review = finding.get("review", {})

        explanation = review.get("explanation", {})
        risk = review.get("risk", {})
        fix = review.get("fix", {})

        vuln_name = explanation.get(
            "vulnerability_type",
            "Security Issue"
        )

        lines.append("---")
        lines.append(f"### 🚨 {vuln_name}")

        lines.append(f"**File:** `{finding['file']}`")
        lines.append(f"**Rule:** `{finding['rule']}`")
        lines.append(f"**Risk:** **{risk.get('risk_level','UNKNOWN')}**\n")

        # Explanation
        lines.append("**Explanation**")
        lines.append(explanation.get("explanation", "No explanation available."))

        # Impact
        if explanation.get("impact"):
            lines.append("\n**Impact**")
            lines.append(explanation.get("impact"))

        # Risk reason
        if risk.get("risk_reason"):
            lines.append("\n**Risk Assessment**")
            lines.append(risk.get("risk_reason"))

        # Fix
        if fix.get("fix_description"):
            lines.append("\n**Suggested Fix**")
            lines.append(fix.get("fix_description"))

        # Code example
        if fix.get("secure_code_example"):
            lines.append("\n```python")
            lines.append(fix.get("secure_code_example"))
            lines.append("```")

        lines.append("")

    return "\n".join(lines)