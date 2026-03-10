import sys

from scanners.semgrep_runner import run_semgrep
from scanners.semgrep_parser import parse_semgrep

from context.diff_analyzer import get_changed_files, tag_new_findings

from knowledge.vulnerability_db import enrich_findings
from knowledge.risk_scoring import compute_risk_score

from llm.adapter import LLMAdapter
from llm.providers.openai_provider import OpenAIProvider

from ai.review_pipeline import ReviewPipeline
from ai.review_aggregator import ReviewAggregator

from reporters.reporter_factory import ReporterFactory

from config import OPENAI_API_KEY


def initialize_ai_pipeline():

    if not OPENAI_API_KEY:
        print("[SecureMR] AI disabled (OPENAI_API_KEY not configured)")
        return None

    provider = OpenAIProvider(api_key=OPENAI_API_KEY)
    llm = LLMAdapter(provider)

    print("[SecureMR] AI analysis enabled")

    return ReviewPipeline(llm)


def load_findings():

    print("[SecureMR] Running Semgrep scan")

    semgrep_results = run_semgrep()

    findings = parse_semgrep(semgrep_results)

    if not findings:
        print("[SecureMR] No findings detected")
        return []

    print(f"[SecureMR] {len(findings)} findings detected")

    changed_files = get_changed_files()

    tag_new_findings(findings, changed_files)

    enrich_findings(findings)

    for finding in findings:
        finding.risk_score = compute_risk_score(finding)

    return findings


def main():

    print("[SecureMR] Starting analysis")

    findings = load_findings()

    if not findings:
        return

    pipeline = initialize_ai_pipeline()

    reporters = ReporterFactory.create()

    aggregator = ReviewAggregator()

    reviews = []

    for finding in findings:

        review = {}

        if pipeline:
            try:
                review = pipeline.run(finding)
            except Exception as e:
                print(f"[SecureMR] AI analysis failed: {e}")

        reviews.append((finding, review))

    report = aggregator.aggregate(reviews)

    for reporter in reporters:
        reporter.publish(report)

    print("[SecureMR] Analysis complete")


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\n[SecureMR] Interrupted")
        sys.exit(1)

    except Exception as e:
        print(f"[SecureMR] Fatal error: {e}")
        sys.exit(1)