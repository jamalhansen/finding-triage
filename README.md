# finding-triage

Routes static-analysis findings to likely owners using `git blame` and a local LLM.

Takes a JSON list of findings (file, line, rule, message), looks up who last touched
each line and what their commit said, and asks a local model to rate urgency and give
a one-line rationale. Sorted output, no ranking by hand.

## Usage

```bash
uv run finding-triage path/to/findings.json --repo path/to/target/repo
```

Findings format:

```json
[
  {"file": "src/thing.py", "line": 42, "rule": "some-rule-id", "message": "what the rule found"}
]
```

## Requirements

- Ollama running locally with a pulled model (defaults to `phi4`)
- `--repo` must be a git repository; blame is skipped (not an error) if it isn't, or if
  the file/line has no history
