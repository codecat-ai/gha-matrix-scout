# Clean-room project brief: gha-matrix-scout

## Research observations (untrusted, no code copied)
- Developers often use GitHub Actions matrix strategies for multiple OS, language versions, regions, and feature variants.
- Matrix expansion can become hard to reason about when includes/excludes are used.
- CI configuration mistakes are often noticed only after pushing to GitHub Actions.
- Documentation and README discussions emphasize practical onboarding, clear examples, and checked local workflows.

## Decision scoring
- Community need / user pain: 8/10
- Originality of angle: 7/10
- MVP usefulness after one run: 7/10
- Testability: 9/10
- Extension potential: 7/10
- Implementation feasibility: 8/10
- Documentation clarity: 8/10
- Abuse/legal/platform risk: low

## Target users
Maintainers and developers who want a local, readable preview of GitHub Actions matrix job combinations before they push workflow changes.

## Problem statement
GitHub Actions matrix jobs are compact but mentally expensive to inspect. A local CLI that expands static matrix definitions and summarizes the generated combinations can catch obvious mistakes early and support README/CI reviews.

## Non-goals
- Do not execute workflows.
- Do not evaluate arbitrary GitHub expression language.
- Do not contact GitHub or require credentials.
- Do not claim perfect parity with GitHub Actions for dynamic expressions.
- Do not publish to package registries.

## MVP features
- Python CLI named `gha-matrix-scout` runnable from a local clone.
- Read one workflow YAML file path.
- Find jobs with `strategy.matrix` mappings.
- Expand cartesian products for static list-valued matrix axes.
- Apply static `exclude` entries by matching exact key/value pairs.
- Apply static `include` entries by adding extra combinations or merging into matching combinations when possible.
- Print a readable text report listing workflow path, jobs, combination counts, and each combination.
- `--json` output with deterministic keys for automation.
- Clear warnings for unsupported dynamic matrix values while still reporting supported jobs.
- Behavior-focused tests for expansion, include/exclude, unsupported values, and CLI output.

## Expected CLI behavior
```bash
python -m gha_matrix_scout path/to/workflow.yml
python -m gha_matrix_scout path/to/workflow.yml --json
```

JSON should include `workflow`, `jobs`, and `warnings`.

## File structure
- `pyproject.toml` with project metadata, pytest, ruff config, and console script.
- `src/gha_matrix_scout/` package with parser, matrix expansion, reporter, CLI, and `__main__.py`.
- `tests/` with behavior tests.
- `README.md`, `README-zh.md`, `README-ja.md` synchronized in meaning.
- `LICENSE` MIT.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- `.github/workflows/ci.yml` running pytest and ruff.
- GitHub issue templates and PR template.

## CI plan
Use Python 3.12 on GitHub Actions. Install with `python -m pip install -e .[dev]`, then run `python -m pytest -q`, `ruff check .`, and `ruff format --check .`.

## README requirements
Document only clone/local usage because no package registry artifact is published. Include problem, features, installation, quick start, examples, configuration, development, testing, roadmap, contributing, MIT license, and a brief AI-assisted maintenance note.
