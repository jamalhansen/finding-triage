from pathlib import Path

from finding_triage.blame import get_blame

# Exercised against this repo itself, which is always a valid git repo when tests run.
REPO = Path(__file__).resolve().parents[1]


def test_get_blame_returns_author_for_tracked_line():
    info = get_blame(REPO, "README.md", 1)
    assert info is not None
    assert info.author
    assert info.author_time > 0


def test_get_blame_returns_none_for_missing_file():
    info = get_blame(REPO, "does-not-exist.py", 1)
    assert info is None
