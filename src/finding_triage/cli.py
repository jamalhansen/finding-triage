"""CLI: read findings, look up blame, score urgency, print sorted results."""

import argparse
import json
import sys
from pathlib import Path

from local_first_common.tracking import register_tool

from finding_triage.blame import get_blame
from finding_triage.llm import assess
from finding_triage.models import Finding, TriageResult

_TOOL = register_tool("finding-triage")

_URGENCY_RANK = {"high": 0, "medium": 1, "low": 2}


def load_findings(path: Path) -> list[Finding]:
    raw = json.loads(path.read_text())
    return [Finding(file=f["file"], line=f["line"], rule=f["rule"], message=f["message"]) for f in raw]


def run(findings_path: Path, repo: Path) -> list[TriageResult]:
    findings = load_findings(findings_path)
    results = []
    for finding in findings:
        blame = get_blame(repo, finding.file, finding.line)
        verdict = assess(finding, blame)
        results.append(
            TriageResult(
                finding=finding,
                blame=blame,
                urgency=verdict["urgency"],
                rationale=verdict["rationale"],
                likely_related_to_recent_change=verdict["likely_related_to_recent_change"],
            )
        )
    results.sort(key=lambda r: _URGENCY_RANK.get(r.urgency, 99))
    return results


def print_results(results: list[TriageResult]) -> None:
    for r in results:
        owner = r.blame.author if r.blame else "unknown"
        print(f"[{r.urgency.upper():6}] {r.finding.file}:{r.finding.line} ({r.finding.rule})")
        print(f"         owner: {owner}")
        print(f"         {r.rationale}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("findings", type=Path, help="JSON file of findings")
    parser.add_argument("--repo", type=Path, default=Path("."), help="git repo the findings apply to")
    args = parser.parse_args()

    if not args.findings.exists():
        print(f"error: {args.findings} not found", file=sys.stderr)
        raise SystemExit(1)

    results = run(args.findings, args.repo)
    print_results(results)


if __name__ == "__main__":
    main()
