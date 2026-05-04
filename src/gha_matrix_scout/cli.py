from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gha_matrix_scout.parser import analyze_workflow
from gha_matrix_scout.reporter import to_jsonable, to_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gha-matrix-scout",
        description="Preview static GitHub Actions matrix combinations.",
    )
    parser.add_argument("workflow", type=Path, help="Path to a workflow YAML file.")
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON."
    )
    args = parser.parse_args(argv)

    try:
        report = analyze_workflow(args.workflow)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Unable to read workflow file: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"Unable to parse workflow file: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(to_jsonable(report), indent=2, sort_keys=False))
    else:
        print(to_text(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
