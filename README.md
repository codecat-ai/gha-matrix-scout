# gha-matrix-scout

`gha-matrix-scout` previews static GitHub Actions matrix job combinations from a local workflow file. It helps maintainers inspect matrix expansions before pushing workflow changes.

## Features

- Reads one workflow YAML file from a local clone.
- Finds jobs with `strategy.matrix` mappings.
- Expands static list-valued matrix axes into cartesian products.
- Applies static `exclude` entries by exact key/value matches.
- Applies static `include` entries by merging into matching combinations or adding new combinations.
- Filters reports to one or more exact job names with repeatable `--job` options.
- Fails CI guardrails with `--max-combinations N` when any reported matrix job expands beyond a positive limit.
- Prints readable text output, concise summary text for CI logs, or deterministic JSON with warnings.
- Warns about unsupported dynamic matrix values without contacting GitHub.

## Installation

Clone this repository and work from the repository root:

```bash
git clone https://github.com/codecat-ai/gha-matrix-scout.git
cd gha-matrix-scout
```

This project is not published to a package registry. Use it from a local clone.

## Quick Start

Run the CLI module against a workflow file:

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml
```

Print JSON for automation:

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --json
```

Print concise one-line-per-job output for CI logs:

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --summary
```

Preview only selected matrix jobs by exact job name:

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --job test --job build
```

Fail the command when any reported matrix job expands beyond a chosen limit:

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --max-combinations 20
```

## Example

For a matrix with two operating systems and two Python versions, plus one excluded pair, the text report lists the workflow path, each matrix job, the final combination count, and each generated combination.

```text
Workflow: .github/workflows/ci.yml

Job: test
Combinations: 3
1. os=ubuntu-latest, python=3.11
2. os=ubuntu-latest, python=3.12
3. os=windows-latest, python=3.12
```

With `--summary`, the same reported jobs are condensed to counts:

```text
test: 3 combinations
```

## Configuration

No network access, GitHub credentials, or workflow execution is required. The scout supports static YAML values only:

- Matrix axes must be lists.
- `exclude` and `include` must be lists of mappings.
- Dynamic expressions are skipped with warnings.
- `--job NAME` filters by exact workflow job name and may be repeated.
- `--summary` prints one line per reported matrix job as `<job-name>: <count> combination(s)`, using `combination` for exactly one combination.
- `--max-combinations N` accepts a positive integer. After normal analysis and any `--job` filtering, the CLI exits with status 1 if a reported matrix job has more than `N` expanded combinations.
- Text and summary modes keep warnings visible. JSON mode keeps valid JSON and adds warning messages to the top-level `warnings` list.
- When `--json` is used, `--summary` is ignored and the JSON shape is unchanged.
- If a `--job` filter matches no matrix jobs, the CLI exits non-zero. Text mode prints an error; JSON mode prints a valid report with the warning.

## Development

The source package lives in `src/gha_matrix_scout/`. Behavior tests live in `tests/`.

Run the behavior suite from the repository root:

```bash
PYTHONPATH=src python -m pytest -q
```

Run formatting and lint checks:

```bash
ruff check .
ruff format --check .
```

## Testing

Tests focus on observable behavior: matrix expansion, include/exclude handling, unsupported values, job filtering, maximum-combination guardrails, text output, summary output, JSON output, and CLI errors.

## Roadmap

- More YAML diagnostics for malformed workflows.
- Richer summary formats for review comments.
- Additional static compatibility checks for matrix definitions.

## Contributing

See `CONTRIBUTING.md`. Keep behavior changes covered by tests and keep the English, Chinese, and Japanese README files synchronized in meaning.

## AI-Assisted Maintenance

AI tools may help draft code, tests, and documentation, but maintainers must review all changes for correctness, originality, licensing, and security before merging.

## License

MIT. See `LICENSE`.
