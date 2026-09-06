"""Local model call that turns a finding + blame context into a triage assessment."""

import json

import ollama

from finding_triage.models import BlameInfo, Finding

_SCHEMA = {
    "type": "object",
    "properties": {
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "rationale": {"type": "string"},
        "likely_related_to_recent_change": {"type": "boolean"},
    },
    "required": ["urgency", "rationale", "likely_related_to_recent_change"],
}

_SYSTEM_PROMPT = """You assess a single static-analysis finding and decide how urgently it needs attention.

You will be given the finding (rule, message, file, line) and, if available, who last touched that
line and what their commit message said.

Rate urgency low/medium/high based on: the rule's likely severity, whether the blamed change looks
recent and related (vs. old unrelated code), and whether the commit summary suggests the author was
already aware of a tradeoff here. Write one concise sentence explaining the rating -- not a summary
of the finding, a reason for the rating."""


def assess(finding: Finding, blame: BlameInfo | None) -> dict:
    if blame is not None:
        blame_text = (
            f"Last changed by {blame.author} <{blame.author_mail}>, "
            f"commit summary: \"{blame.summary}\""
        )
    else:
        blame_text = "No blame information available for this line."

    user_prompt = (
        f"Finding: [{finding.rule}] {finding.message}\n"
        f"Location: {finding.file}:{finding.line}\n"
        f"{blame_text}"
    )

    response = ollama.chat(
        model="phi4",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        format=_SCHEMA,
    )
    return json.loads(response["message"]["content"])
