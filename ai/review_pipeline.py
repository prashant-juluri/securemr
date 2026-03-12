from ai.explain_agent import ExplainAgent
from ai.risk_agent import RiskAgent
from ai.fix_agent import FixAgent


class ReviewPipeline:

    def __init__(self, llm):

        self.explain_agent = ExplainAgent(llm)
        self.risk_agent = RiskAgent(llm)
        self.fix_agent = FixAgent(llm)

    def run(self, finding):
        """
        Run the AI review pipeline for a finding.
        """

        explanation_result = {}
        risk_result = {}
        fix_result = {}

        # Step 1 — Explain vulnerability
        try:
            explanation_result = self.explain_agent.analyze(finding)
        except Exception as e:
            explanation_result = {
                "error": "explain_agent_failed",
                "details": str(e.__traceback__)
            }

        explanation_text = explanation_result.get("explanation", "")

        # Step 2 — Risk analysis
        try:
            risk_result = self.risk_agent.analyze(
                finding,
                explanation_text
            )
        except Exception as e:
            risk_result = {
                "error": "risk_agent_failed",
                "details": str(e.__traceback__)
            }

        # Step 3 — Fix generation
        try:
            fix_result = self.fix_agent.analyze(finding)
        except Exception as e:
            fix_result = {
                "error": "fix_agent_failed",
                "details": str(e.__traceback__)
            }

        return {
            "explanation": explanation_result,
            "risk": risk_result,
            "fix": fix_result
        }