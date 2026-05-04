from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gha_matrix_scout.parser import WorkflowReport, analyze_workflow
from gha_matrix_scout.reporter import to_jsonable, to_text


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "--max-combinations must be a positive integer"
        ) from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            "--max-combinations must be a positive integer"
        )
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gha-matrix-scout",
        description="Preview static GitHub Actions matrix combinations.",
    )
    parser.add_argument("workflow", type=Path, help="Path to a workflow YAML file.")
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON."
    )
    parser.add_argument(
        "--job",
        action="append",
        default=[],
        metavar="NAME",
        help="Preview only matrix jobs whose names exactly match NAME. Repeatable.",
    )
    parser.add_argument(
        "--max-combinations",
        type=_positive_int,
        metavar="N",
        help=(
            "Exit non-zero if any reported matrix job expands to more than "
            "N combinations."
        ),
    )
    args = parser.parse_args(argv)

    try:
        report = analyze_workflow(args.workflow, job_names=args.job)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Unable to read workflow file: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"Unable to parse workflow file: {error}", file=sys.stderr)
        return 2

    if args.job and not report.jobs:
        filters = ", ".join(args.job)
        warning = f"No matrix jobs matched --job filter: {filters}"
        report = WorkflowReport(
            workflow=report.workflow,
            jobs=report.jobs,
            warnings=[*report.warnings, warning],
        )
        if args.json:
            print(json.dumps(to_jsonable(report), indent=2, sort_keys=False))
        else:
            print(warning, file=sys.stderr)
        return 1

    exit_status = 0
    if args.max_combinations is not None:
        limit_warnings = [
            (
                f"Job {job.name} has {len(job.combinations)} combinations, "
                f"exceeding --max-combinations {args.max_combinations}."
            )
            for job in report.jobs
            if len(job.combinations) > args.max_combinations
        ]
        if limit_warnings:
            exit_status = 1
            report = WorkflowReport(
                workflow=report.workflow,
                jobs=report.jobs,
                warnings=[*report.warnings, *limit_warnings],
            )

    if args.json:
        print(json.dumps(to_jsonable(report), indent=2, sort_keys=False))
    else:
        print(to_text(report), end="")
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
