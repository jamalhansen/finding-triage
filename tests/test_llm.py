import json

from local_first_common.testing import MockProvider

from finding_triage.llm import assess
from finding_triage.models import BlameInfo, Finding


def _mock(urgency="high", rationale="test reason", related=True):
    return MockProvider(
        response=json.dumps(
            {
                "urgency": urgency,
                "rationale": rationale,
                "likely_related_to_recent_change": related,
            }
        )
    )


class TestAssess:
    def test_returns_dict_with_expected_fields(self):
        finding = Finding(file="foo.py", line=10, rule="BLE001", message="blind except")
        blame = BlameInfo(
            author="Jamal", author_mail="j@example.com", summary="fix stuff", author_time="2026-09-10"
        )
        result = assess(finding, blame, provider=_mock())
        assert result == {
            "urgency": "high",
            "rationale": "test reason",
            "likely_related_to_recent_change": True,
        }

    def test_handles_missing_blame(self):
        finding = Finding(file="foo.py", line=10, rule="BLE001", message="blind except")
        result = assess(finding, None, provider=_mock(urgency="low", related=False))
        assert result["urgency"] == "low"
        assert result["likely_related_to_recent_change"] is False
