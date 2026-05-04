from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from gha_matrix_scout.matrix import expand_matrix


@dataclass(frozen=True)
class JobReport:
    name: str
    combinations: list[dict[str, Any]]


@dataclass(frozen=True)
class WorkflowReport:
    workflow: str
    jobs: list[JobReport]
    warnings: list[str]


def analyze_workflow(path: str | Path) -> WorkflowReport:
    workflow_path = Path(path)
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    data = yaml.safe_load(workflow_path.read_text(encoding="utf-8")) or {}
    jobs_data = data.get("jobs", {})
    reports: list[JobReport] = []
    warnings: list[str] = []

    if not isinstance(jobs_data, dict):
        return WorkflowReport(
            str(workflow_path), reports, ["Workflow jobs must be a mapping."]
        )

    for job_name, job_data in jobs_data.items():
        matrix = _matrix_for_job(job_data)
        if matrix is None:
            continue
        if not isinstance(matrix, dict):
            warnings.append(
                f"Job '{job_name}' strategy.matrix is not a static mapping."
            )
            continue

        expansion = expand_matrix(matrix, str(job_name))
        reports.append(
            JobReport(name=str(job_name), combinations=expansion.combinations)
        )
        warnings.extend(expansion.warnings)

    return WorkflowReport(workflow=str(workflow_path), jobs=reports, warnings=warnings)


def _matrix_for_job(job_data: Any) -> Any | None:
    if not isinstance(job_data, dict):
        return None
    strategy = job_data.get("strategy")
    if not isinstance(strategy, dict):
        return None
    return strategy.get("matrix")
