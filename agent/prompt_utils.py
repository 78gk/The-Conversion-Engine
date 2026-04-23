from __future__ import annotations

from typing import Any

from core.project_adapter import ProjectAdapter


def load_previous_metrics(adapter: ProjectAdapter) -> dict[str, Any] | None:
    try:
        data = adapter.read_json("memory/metrics.json", default=None)
    except ValueError:
        return None

    if not isinstance(data, dict):
        return None
    return data


def render_previous_metrics_section(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return ""

    status = metrics.get("status", "unknown")
    pass_at_1 = metrics.get("pass@1", "n/a")
    return (
        "\n"
        "Previous Run Signals:\n"
        f"- status: {status}\n"
        f"- pass@1: {pass_at_1}\n"
        "- use these only as guidance; do not overfit to one run\n"
    )


def render_requirements_block() -> str:
    return (
        "Requirements:\n"
        "- production ready code\n"
        "- proper structure\n"
        "- include error handling\n\n"
        "DO NOT:\n"
        "- add unnecessary features\n\n"
    )
