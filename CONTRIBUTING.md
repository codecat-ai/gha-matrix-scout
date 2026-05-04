# Contributing

Thank you for improving `gha-matrix-scout`. This project values small, well-tested changes that are easy to review.

## Development Principles

- Keep behavior changes covered by tests.
- Prefer clear, local code over broad abstractions.
- Do not execute workflows or contact GitHub from the scout.
- Keep comments and commit messages in English.
- Keep `README.md`, `README-zh.md`, and `README-jp.md` synchronized in meaning.
- Do not copy code or prose from other projects without a clear compatible license and attribution.

## Local Checks

Run tests and checks from the repository root:

```bash
PYTHONPATH=src python -m pytest -q
ruff check .
ruff format --check .
```

## Pull Requests

Include a short summary, test results, and any behavior or documentation changes. Use Conventional Commit style for commits when practical.

## Security

Do not include secrets, tokens, or private workflow contents in issues or pull requests. Report sensitive concerns privately to the maintainers when a private contact is available.
