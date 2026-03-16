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
from security.baseline import mark_new_findings, save_baseline
from llm.provider_factory import ProviderFactory

from config import OPENAI_API_KEY


def initialize_ai_pipeline():

    if not OPENAI_API_KEY:
        print("[SecureMR] AI disabled (OPENAI_API_KEY not configured)")
        return None

    provider = ProviderFactory.create()
    llm = LLMAdapter(provider)

    print("[SecureMR] AI analysis enabled")

    return ReviewPipeline(llm)


def load_findings(target_path):

    print(f"[SecureMR] Running Semgrep scan on: {target_path}")

    semgrep_results = run_semgrep(target_path)

    findings = parse_semgrep(semgrep_results)

    if not findings:
        print("[SecureMR] No findings detected")
        return []

    print(f"[SecureMR] {len(findings)} findings detected")
    

    try:
        changed_files = get_changed_files()
        tag_new_findings(findings, changed_files)
        if changed_files is None:
            filtered_findings = findings
        else:
            filtered_findings = [f for f in findings if f.new_issue]

        print(f"[SecureMR] {len(filtered_findings)} findings detected in the current diff")
    except Exception:
        print("[SecureMR] Unable to determine git diff. Marking all findings as existing.")

    #print(f"[SecureMR] {len(findings)} findings detected in the current diff")

    print("[SecureMR] Checking for new vulnerabilities")

    new_findings = mark_new_findings(filtered_findings)

    print(f"[SecureMR] {len(new_findings)} new findings identified in the current PR/MR")

    enrich_findings(new_findings)

    for finding in new_findings:
        finding.risk_score = compute_risk_score(finding)

    return new_findings


def main():

    print("[SecureMR] Starting analysis")
    reporters = ReporterFactory.create()

    aggregator = ReviewAggregator()

    # Accept target path from CLI
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."

    findings = load_findings(target_path)

    if not findings:
        print("[SecureMR] Analysis complete (no findings)")
        return

    pipeline = initialize_ai_pipeline()

    

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
        try:
            reporter.publish(report)
        except Exception as e:
            print(f"[SecureMR] Reporter failed: {e}")

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