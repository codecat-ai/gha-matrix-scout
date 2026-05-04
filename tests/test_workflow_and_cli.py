import json
import subprocess
import sys

from gha_matrix_scout.parser import analyze_workflow
from gha_matrix_scout.reporter import to_jsonable, to_summary_text, to_text

WORKFLOW = """
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.11", "3.12"]
        exclude:
          - os: windows-latest
            python: "3.11"
        include:
          - os: ubuntu-latest
            python: "3.12"
            experimental: true
  lint:
    runs-on: ubuntu-latest
  dynamic:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: ${{ fromJSON(inputs.node_versions) }}
        os: [ubuntu-latest]
"""

LIMIT_WORKFLOW = """
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.11", "3.12", "3.13"]
  smoke:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest]
        python: ["3.12"]
"""

SINGLE_AND_EMPTY_WORKFLOW = """
name: CI
on: [push]
jobs:
  smoke:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest]
  lint:
    runs-on: ubuntu-latest
"""


def test_analyzes_workflow_jobs_and_warnings(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    report = analyze_workflow(workflow)

    assert report.workflow == str(workflow)
    assert [job.name for job in report.jobs] == ["test", "dynamic"]
    assert len(report.jobs[0].combinations) == 3
    assert report.jobs[1].combinations == [{"os": "ubuntu-latest"}]
    assert report.warnings == [
        "Job 'dynamic' matrix axis 'node' is not a static list and was skipped."
    ]


def test_text_report_is_readable_and_deterministic(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    text = to_text(analyze_workflow(workflow))

    assert f"Workflow: {workflow}" in text
    assert "Job: test" in text
    assert "Combinations: 3" in text
    assert "1. os=ubuntu-latest, python=3.11" in text
    assert "2. experimental=true, os=ubuntu-latest, python=3.12" in text
    assert "Warnings:" in text


def test_summary_report_lists_only_job_counts(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    text = to_summary_text(analyze_workflow(workflow))

    assert text == "test: 6 combinations\nsmoke: 1 combination\n"


def test_summary_report_keeps_no_jobs_message_single_line(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(SINGLE_AND_EMPTY_WORKFLOW, encoding="utf-8")

    text = to_summary_text(analyze_workflow(workflow, job_names=["lint"]))

    assert text == "No jobs with static strategy.matrix mappings found.\n"


def test_summary_report_keeps_warnings_visible(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    text = to_summary_text(analyze_workflow(workflow))

    assert "Warnings:" in text
    assert (
        "- Job 'dynamic' matrix axis 'node' is not a static list and was skipped."
        in text
    )


def test_json_report_uses_stable_shape(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    data = to_jsonable(analyze_workflow(workflow))

    assert list(data) == ["workflow", "jobs", "warnings"]
    assert data["jobs"][0] == {
        "name": "test",
        "combination_count": 3,
        "combinations": [
            {"os": "ubuntu-latest", "python": "3.11"},
            {"experimental": True, "os": "ubuntu-latest", "python": "3.12"},
            {"os": "windows-latest", "python": "3.12"},
        ],
    }


def test_cli_outputs_json(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "gha_matrix_scout", str(workflow), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(completed.stdout)
    assert data["workflow"] == str(workflow)
    assert data["jobs"][0]["name"] == "test"
    assert data["warnings"] == [
        "Job 'dynamic' matrix axis 'node' is not a static list and was skipped."
    ]


def test_cli_max_combinations_reports_text_over_limit_after_normal_report(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--max-combinations",
            "4",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "Job: test" in completed.stdout
    assert "Combinations: 6" in completed.stdout
    assert (
        "Job test has 6 combinations, exceeding --max-combinations 4."
        in completed.stdout
    )
    assert completed.stderr == ""


def test_cli_summary_outputs_one_line_per_reported_matrix_job(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "gha_matrix_scout", str(workflow), "--summary"],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = completed.stdout.splitlines()
    assert lines[:2] == ["test: 3 combinations", "dynamic: 1 combination"]
    assert "Workflow:" not in completed.stdout
    assert "Job:" not in completed.stdout
    assert "Combinations:" not in completed.stdout


def test_cli_summary_composes_with_job_filter(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--summary",
            "--job",
            "dynamic",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.splitlines()[0] == "dynamic: 1 combination"
    assert "test: 3 combinations" not in completed.stdout


def test_cli_summary_max_combinations_keeps_warning_visible(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--summary",
            "--max-combinations",
            "4",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "test: 6 combinations" in completed.stdout
    assert "smoke: 1 combination" in completed.stdout
    assert (
        "Job test has 6 combinations, exceeding --max-combinations 4."
        in completed.stdout
    )
    assert completed.stderr == ""


def test_cli_json_ignores_summary_presentation_option(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--json",
            "--summary",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(completed.stdout)
    assert list(data) == ["workflow", "jobs", "warnings"]
    assert data["jobs"][0]["combination_count"] == 3
    assert "combinations" in data["jobs"][0]


def test_cli_max_combinations_reports_json_over_limit(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--max-combinations",
            "4",
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    data = json.loads(completed.stdout)
    assert data["jobs"][0]["name"] == "test"
    assert data["jobs"][0]["combination_count"] == 6
    assert data["warnings"] == [
        "Job test has 6 combinations, exceeding --max-combinations 4."
    ]
    assert completed.stderr == ""


def test_cli_max_combinations_within_limit_keeps_success_behavior(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--max-combinations",
            "6",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Job: test" in completed.stdout
    assert "Combinations: 6" in completed.stdout
    assert "exceeding --max-combinations" not in completed.stdout
    assert completed.stderr == ""


def test_cli_max_combinations_rejects_invalid_values(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    for value in ["0", "-1", "many"]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "gha_matrix_scout",
                str(workflow),
                "--max-combinations",
                value,
            ],
            capture_output=True,
            text=True,
        )

        assert completed.returncode != 0
        assert "--max-combinations must be a positive integer" in completed.stderr


def test_cli_max_combinations_checks_only_selected_jobs(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(LIMIT_WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--job",
            "smoke",
            "--max-combinations",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Job: smoke" in completed.stdout
    assert "Job: test" not in completed.stdout
    assert "exceeding --max-combinations" not in completed.stdout
    assert completed.stderr == ""


def test_cli_filters_to_requested_job(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "gha_matrix_scout", str(workflow), "--job", "dynamic"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Job: dynamic" in completed.stdout
    assert "Job: test" not in completed.stdout
    assert "node" in completed.stdout


def test_cli_reports_no_matching_jobs_in_text_mode(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "gha_matrix_scout", str(workflow), "--job", "release"],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "No matrix jobs matched --job filter: release" in completed.stderr
    assert completed.stdout == ""


def test_cli_reports_no_matching_jobs_as_json(tmp_path):
    workflow = tmp_path / "workflow.yml"
    workflow.write_text(WORKFLOW, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gha_matrix_scout",
            str(workflow),
            "--job",
            "release",
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    data = json.loads(completed.stdout)
    assert data["jobs"] == []
    assert data["warnings"] == ["No matrix jobs matched --job filter: release"]
    assert completed.stderr == ""


def test_cli_reports_missing_file(tmp_path):
    missing = tmp_path / "missing.yml"

    completed = subprocess.run(
        [sys.executable, "-m", "gha_matrix_scout", str(missing)],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "Workflow file not found" in completed.stderr
