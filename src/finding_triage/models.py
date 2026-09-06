"""Data shapes for findings, blame context, and triage results."""

from dataclasses import dataclass


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    message: str


@dataclass
class BlameInfo:
    author: str
    author_mail: str
    author_time: int
    summary: str


@dataclass
class TriageResult:
    finding: Finding
    blame: BlameInfo | None
    urgency: str  # "low" | "medium" | "high"
    rationale: str
    likely_related_to_recent_change: bool
