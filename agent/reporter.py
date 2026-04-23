from pathlib import Path

from core.project_adapter import ProjectAdapter


DEFAULT_ADAPTER = ProjectAdapter(Path(__file__).resolve().parents[1])


def run(adapter: ProjectAdapter | None = None):
    adapter = adapter or DEFAULT_ADAPTER
    print("Generating report...")

    metrics = adapter.read_json("memory/metrics.json", default={})
    status = metrics.get("status", "unknown")
    pass_at_1 = metrics.get("pass@1", "n/a")
    details = metrics.get("details", {}) if isinstance(metrics, dict) else {}
    failed_required = details.get("failed_required_checks", []) if isinstance(details, dict) else []

    report_lines = [
        "# Project Report",
        "",
        f"- Evaluation status: {status}",
        f"- pass@1: {pass_at_1}",
        "",
        "## Summary",
        "- Workflow executed from planning through reporting.",
        "- Interim requirements are evaluated as explicit checks.",
    ]

    if failed_required:
        report_lines.extend([
            "",
            "## Missing Interim Requirements",
        ])
        report_lines.extend(f"- {item}" for item in failed_required)
    else:
        report_lines.extend([
            "",
            "## Missing Interim Requirements",
            "- none",
        ])

    report = "\n".join(report_lines) + "\n"

    adapter.write_text_if_changed("artifacts/reports/README.md", report.strip() + "\n")

    return {"status": "success", "report_path": "artifacts/reports/README.md"}
