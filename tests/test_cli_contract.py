"""The command-line contract for finding-triage, as golden output (paths that call no LLM).

Re-record deliberately with RECORD_CLI_CONTRACT=1.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

GOLDEN = Path(__file__).parent / "golden" / "cli_contract.json"
SCRIPT = Path(sys.executable).parent / "finding-triage"
CASES = [
    ["{T}/empty.json"],
    ["{T}/empty.json", "--repo", "{T}"],
    ["{T}/missing.json"],
    [],
    ["{T}/empty.json", "--nope"],
]


def test_cli_contract(tmp_path):
    (tmp_path / "empty.json").write_text("[]")
    env = {**os.environ, "LOCAL_FIRST_TRACKING_DB": str(tmp_path / "tracking.duckdb")}
    results = []
    for argv in CASES:
        args = [a.replace("{T}", str(tmp_path)) for a in argv]
        proc = subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, env=env, check=False)
        r = {"argv": argv, "exit": proc.returncode}
        if proc.returncode != 2:
            r["stdout"] = proc.stdout.replace(str(tmp_path), "<TMP>")
            r["stderr"] = proc.stderr.replace(str(tmp_path), "<TMP>")
        results.append(r)
    if os.environ.get("RECORD_CLI_CONTRACT"):
        GOLDEN.write_text(json.dumps(results, indent=2) + "\n")
        pytest.skip("recorded")
    assert results == json.loads(GOLDEN.read_text())


def test_findings_are_triaged_and_sorted(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    from finding_triage import cli

    f = tmp_path / "f.json"
    f.write_text(json.dumps([
        {"file": "a.py", "line": 1, "rule": "R1", "message": "m1"},
        {"file": "b.py", "line": 2, "rule": "R2", "message": "m2"},
    ]))
    monkeypatch.setattr(cli, "get_blame", lambda repo, file, line: None)
    verdicts = {"R1": "low", "R2": "high"}
    monkeypatch.setattr(cli, "assess", lambda finding, blame: {
        "urgency": verdicts[finding.rule], "rationale": "because", "likely_related_to_recent_change": False})
    result = CliRunner().invoke(cli.app, [str(f)])
    assert result.exit_code == 0, result.output
    assert result.output.index("[HIGH") < result.output.index("[LOW")
