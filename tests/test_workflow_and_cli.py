import json
import subprocess
import sys

from gha_matrix_scout.parser import analyze_workflow
from gha_matrix_scout.reporter import to_jsonable, to_text

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
