from scanners.semgrep_parser import parse_semgrep
from context.diff_analyzer import get_changed_files, tag_new_findings


def main():

    findings = parse_semgrep("sample_findings/semgrep.json")

    changed = get_changed_files()

    tag_new_findings(findings, changed)

    for f in findings:
        print(f.file, f.rule, f.new_issue)


if __name__ == "__main__":
    main()