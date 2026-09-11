"""Local model call that turns a finding + blame context into a triage assessment."""

from local_first_common.cli import resolve_provider
from local_first_common.providers.base import BaseProvider
from pydantic import BaseModel

from finding_triage.models import BlameInfo, Finding

_SYSTEM_PROMPT = """You assess a single static-analysis finding and decide how urgently it needs attention.

You will be given the finding (rule, message, file, line) and, if available, who last touched that
line and what their commit message said.

Rate urgency low/medium/high based on: the rule's likely severity, whether the blamed change looks
recent and related (vs. old unrelated code), and whether the commit summary suggests the author was
already aware of a tradeoff here. Write one concise sentence explaining the rating -- not a summary
of the finding, a reason for the rating."""


class TriageAssessment(BaseModel):
    urgency: str
    rationale: str
    likely_related_to_recent_change: bool


def assess(finding: Finding, blame: BlameInfo | None, provider: BaseProvider | None = None) -> dict:
    if provider is None:
        provider = resolve_provider(provider_name="ollama", model="phi4")

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

    result = provider.complete(_SYSTEM_PROMPT, user_prompt, response_model=TriageAssessment)
    return result.model_dump()
