"""CLI: read findings, look up blame, score urgency, print sorted results."""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
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


app = typer.Typer(help=__doc__, add_completion=False)


@app.command()
def main(
    findings: Annotated[Path, typer.Argument(help="JSON file of findings")],
    repo: Annotated[Path, typer.Option("--repo", help="git repo the findings apply to")] = Path("."),
) -> None:
    """Read findings, look up blame, score urgency, print sorted results."""
    if not findings.exists():
        print(f"error: {findings} not found", file=sys.stderr)
        raise typer.Exit(1)

    results = run(findings, repo)
    print_results(results)


if __name__ == "__main__":
    app()
