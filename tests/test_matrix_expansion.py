from gha_matrix_scout.matrix import expand_matrix


def test_expands_static_axes_in_deterministic_order():
    result = expand_matrix(
        {
            "os": ["ubuntu-latest", "macos-latest"],
            "python": ["3.11", "3.12"],
        },
        job_name="test",
    )

    assert result.combinations == [
        {"os": "ubuntu-latest", "python": "3.11"},
        {"os": "ubuntu-latest", "python": "3.12"},
        {"os": "macos-latest", "python": "3.11"},
        {"os": "macos-latest", "python": "3.12"},
    ]
    assert result.warnings == []


def test_applies_exclude_and_include_entries():
    result = expand_matrix(
        {
            "os": ["ubuntu-latest", "windows-latest"],
            "python": ["3.11", "3.12"],
            "exclude": [{"os": "windows-latest", "python": "3.11"}],
            "include": [
                {"os": "ubuntu-latest", "python": "3.12", "experimental": True},
                {"os": "macos-latest", "python": "3.12"},
            ],
        },
        job_name="test",
    )

    assert result.combinations == [
        {"os": "ubuntu-latest", "python": "3.11"},
        {"experimental": True, "os": "ubuntu-latest", "python": "3.12"},
        {"os": "windows-latest", "python": "3.12"},
        {"os": "macos-latest", "python": "3.12"},
    ]
    assert result.warnings == []


def test_warns_and_skips_unsupported_dynamic_axes():
    result = expand_matrix(
        {
            "os": ["ubuntu-latest"],
            "python": "${{ fromJSON(inputs.versions) }}",
        },
        job_name="test",
    )

    assert result.combinations == [{"os": "ubuntu-latest"}]
    assert result.warnings == [
        "Job 'test' matrix axis 'python' is not a static list and was skipped."
    ]
