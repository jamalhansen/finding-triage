"""Git blame lookups for a single file/line."""

import subprocess
from pathlib import Path

from finding_triage.models import BlameInfo


def get_blame(repo: Path, file: str, line: int) -> BlameInfo | None:
    result = subprocess.run(
        ["git", "-C", str(repo), "blame", "-L", f"{line},{line}", "--porcelain", "--", file],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    lines = result.stdout.splitlines()
    author = ""
    author_mail = ""
    author_time = 0
    summary = ""
    for raw in lines:
        if raw.startswith("author "):
            author = raw[len("author ") :]
        elif raw.startswith("author-mail "):
            author_mail = raw[len("author-mail ") :].strip("<>")
        elif raw.startswith("author-time "):
            author_time = int(raw[len("author-time ") :])
        elif raw.startswith("summary "):
            summary = raw[len("summary ") :]

    if not author:
        return None

    return BlameInfo(author=author, author_mail=author_mail, author_time=author_time, summary=summary)
