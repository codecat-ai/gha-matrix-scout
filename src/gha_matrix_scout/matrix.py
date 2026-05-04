from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

RESERVED_KEYS = {"include", "exclude"}


@dataclass(frozen=True)
class MatrixExpansion:
    combinations: list[dict[str, Any]]
    warnings: list[str]


def expand_matrix(matrix: dict[str, Any], job_name: str) -> MatrixExpansion:
    axes: dict[str, list[Any]] = {}
    warnings: list[str] = []

    for key, value in matrix.items():
        if key in RESERVED_KEYS:
            continue
        if isinstance(value, list):
            axes[key] = value
        else:
            message = (
                f"Job '{job_name}' matrix axis '{key}' is not a static list "
                "and was skipped."
            )
            warnings.append(message)

    combinations = _cartesian_product(axes)
    combinations = _apply_excludes(
        combinations, matrix.get("exclude", []), job_name, warnings
    )
    combinations = _apply_includes(
        combinations, matrix.get("include", []), job_name, warnings
    )

    return MatrixExpansion(
        combinations=[_sorted_mapping(combination) for combination in combinations],
        warnings=warnings,
    )


def _cartesian_product(axes: dict[str, list[Any]]) -> list[dict[str, Any]]:
    if not axes:
        return []

    axis_names = list(axes)
    return [
        dict(zip(axis_names, values, strict=True))
        for values in product(*(axes[name] for name in axis_names))
    ]


def _apply_excludes(
    combinations: list[dict[str, Any]],
    excludes: Any,
    job_name: str,
    warnings: list[str],
) -> list[dict[str, Any]]:
    if excludes in (None, []):
        return combinations
    if not _is_list_of_mappings(excludes):
        warnings.append(
            f"Job '{job_name}' matrix exclude entries are not static mappings."
        )
        return combinations

    return [
        combination
        for combination in combinations
        if not any(_matches_subset(combination, exclude) for exclude in excludes)
    ]


def _apply_includes(
    combinations: list[dict[str, Any]],
    includes: Any,
    job_name: str,
    warnings: list[str],
) -> list[dict[str, Any]]:
    if includes in (None, []):
        return combinations
    if not _is_list_of_mappings(includes):
        warnings.append(
            f"Job '{job_name}' matrix include entries are not static mappings."
        )
        return combinations

    expanded = [dict(combination) for combination in combinations]
    for include in includes:
        matched = False
        for index, combination in enumerate(expanded):
            if _can_merge(combination, include):
                expanded[index] = {**combination, **include}
                matched = True
        if not matched:
            expanded.append(dict(include))
    return expanded


def _matches_subset(combination: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(combination.get(key) == value for key, value in expected.items())


def _can_merge(combination: dict[str, Any], include: dict[str, Any]) -> bool:
    overlap = set(combination) & set(include)
    return bool(overlap) and all(combination[key] == include[key] for key in overlap)


def _is_list_of_mappings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, dict) for item in value)


def _sorted_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: mapping[key] for key in sorted(mapping)}
