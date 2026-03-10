class ReviewAggregator:

    def aggregate(self, reviews):

        report = {
            "total_findings": len(reviews),
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "findings": []
        }

        for finding, review in reviews:

            risk = review.get("risk", {})
            risk_level = risk.get("risk_level", "").upper()

            if risk_level in ["HIGH", "CRITICAL"]:
                report["high_risk"] += 1

            elif risk_level == "MEDIUM":
                report["medium_risk"] += 1

            else:
                report["low_risk"] += 1

            report["findings"].append({
                "file": finding.file,
                "rule": finding.rule,
                "cwe": finding.cwe,
                "risk": risk_level,
                "review": review
            })

        return report