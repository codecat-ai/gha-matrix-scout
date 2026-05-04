from __future__ import annotations

from typing import Any

from gha_matrix_scout.parser import WorkflowReport


def to_jsonable(report: WorkflowReport) -> dict[str, Any]:
    return {
        "workflow": report.workflow,
        "jobs": [
            {
                "name": job.name,
                "combination_count": len(job.combinations),
                "combinations": job.combinations,
            }
            for job in report.jobs
        ],
        "warnings": report.warnings,
    }


def to_text(report: WorkflowReport) -> str:
    lines = [f"Workflow: {report.workflow}", ""]

    if report.jobs:
        for job in report.jobs:
            lines.append(f"Job: {job.name}")
            lines.append(f"Combinations: {len(job.combinations)}")
            if job.combinations:
                for index, combination in enumerate(job.combinations, start=1):
                    lines.append(f"{index}. {_format_combination(combination)}")
            else:
                lines.append("(no static combinations)")
            lines.append("")
    else:
        lines.extend(["No jobs with static strategy.matrix mappings found.", ""])

    if report.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report.warnings)

    return "\n".join(lines).rstrip() + "\n"


def _format_combination(combination: dict[str, Any]) -> str:
    return ", ".join(
        f"{key}={_format_value(value)}" for key, value in combination.items()
    )


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
