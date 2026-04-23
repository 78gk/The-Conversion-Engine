"""Evaluation script for the Conversion Engine workspace.

This script performs a narrow, production-style validation of the current build:
it checks that the generated artifacts exist, reads the latest metrics, and
emits a structured evaluation result. It is intentionally conservative and does
not invent additional scoring logic beyond the workspace's current outputs.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


class EvaluationError(RuntimeError):
    """Raised when the evaluation cannot complete successfully."""


@dataclass(frozen=True)
class EvaluationConfig:
    project_root: Path

    @property
    def memory_metrics_path(self) -> Path:
        return self.project_root / "memory" / "metrics.json"

    @property
    def report_path(self) -> Path:
        return self.project_root / "artifacts" / "reports" / "README.md"

    @property
    def build_prompt_dir(self) -> Path:
        return self.project_root / "artifacts" / "prompts"

    @property
    def tasks_path(self) -> Path:
        return self.project_root / "memory" / "tasks.json"

    @property
    def code_dir(self) -> Path:
        return self.project_root / "agent"

    @property
    def improve_prompt_path(self) -> Path:
        return self.build_prompt_dir / "improve.txt"

    @property
    def fix_prompt_path(self) -> Path:
        return self.build_prompt_dir / "fix.txt"

    @property
    def requirements_summary_path(self) -> Path:
        return self.project_root / "artifacts" / "reports" / "requirements_summary.md"

    @property
    def readme_path(self) -> Path:
        return self.project_root / "README.md"

    @property
    def eval_dir(self) -> Path:
        return self.project_root / "eval"

    @property
    def score_log_path(self) -> Path:
        return self.eval_dir / "score_log.json"

    @property
    def trace_log_path(self) -> Path:
        return self.eval_dir / "trace_log.jsonl"

    @property
    def baseline_path(self) -> Path:
        return self.project_root / "baseline.md"

    @property
    def interim_report_path(self) -> Path:
        return self.project_root / "artifacts" / "reports" / "INTERIM_DAY3_REPORT.md"

    @property
    def interim_instructions_path(self) -> Path:
        return self.project_root / "input" / "TRP1 Challenge Week 10_ Conversion Engine for Sales Automation.md"


@dataclass(frozen=True)
class EvaluationResult:
    status: str
    pass_at_1: float | None
    prompt_count: int
    report_exists: bool
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "pass@1": self.pass_at_1,
            "prompt_count": self.prompt_count,
            "report_exists": self.report_exists,
            "details": self.details,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the current workspace outputs.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the workspace root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the evaluation result as JSON.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvaluationError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"Invalid JSON in {path}") from exc
    except OSError as exc:
        raise EvaluationError(f"Unable to read {path}") from exc

    return data


def count_prompt_files(prompt_dir: Path) -> int:
    if not prompt_dir.exists():
        return 0
    return sum(1 for path in prompt_dir.glob("task_*.txt") if path.is_file())


def load_tasks(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not isinstance(data, list):
        raise EvaluationError(f"Expected JSON list in {path}")

    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise EvaluationError(f"Task entry {index} in {path} is not an object")
        task_name = item.get("task")
        if not isinstance(task_name, str) or not task_name.strip():
            raise EvaluationError(f"Task entry {index} in {path} has invalid 'task'")
        tasks.append(item)
    return tasks


def prompt_has_required_sections(prompt_text: str) -> bool:
    required_markers = ["Requirements:", "DO NOT:", "include error handling"]
    return all(marker in prompt_text for marker in required_markers)


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EvaluationError(f"Unable to read prompt file: {path}") from exc


def evaluate(config: EvaluationConfig) -> EvaluationResult:
    prompt_count = count_prompt_files(config.build_prompt_dir)
    report_exists = config.report_path.exists()
    tasks = load_tasks(config.tasks_path)

    checks: dict[str, bool] = {
        "task_manifest_loaded": True,
        "task_prompts_count_matches_tasks": prompt_count == len(tasks),
        "interim_instructions_present": config.interim_instructions_path.exists(),
        "readme_exists": config.readme_path.exists(),
        "eval_dir_exists": config.eval_dir.exists(),
        "score_log_exists": config.score_log_path.exists(),
        "trace_log_exists": config.trace_log_path.exists(),
        "baseline_exists": config.baseline_path.exists(),
        "interim_report_exists": config.interim_report_path.exists(),
        "report_exists": report_exists,
        "requirements_summary_exists": config.requirements_summary_path.exists(),
        "improve_prompt_exists": config.improve_prompt_path.exists(),
        "fix_prompt_exists": config.fix_prompt_path.exists(),
        "code_artifact_conversion_engine_exists": (config.code_dir / "conversion_engine.py").exists(),
        "code_artifact_evaluation_script_exists": (config.code_dir / "evaluation_script.py").exists(),
    }

    missing_task_prompts: list[str] = []
    malformed_task_prompts: list[str] = []
    for index, task in enumerate(tasks):
        prompt_path = config.build_prompt_dir / f"task_{index}.txt"
        text = read_text_if_exists(prompt_path)
        if text is None:
            missing_task_prompts.append(prompt_path.name)
            continue

        expected_task_line = f"Task: {task['task']}"
        if expected_task_line not in text or not prompt_has_required_sections(text):
            malformed_task_prompts.append(prompt_path.name)

    checks["all_task_prompts_present"] = len(missing_task_prompts) == 0
    checks["all_task_prompts_well_formed"] = len(malformed_task_prompts) == 0

    improve_text = read_text_if_exists(config.improve_prompt_path)
    fix_text = read_text_if_exists(config.fix_prompt_path)
    checks["improve_prompt_has_focus"] = bool(improve_text and "Focus:" in improve_text)
    checks["fix_prompt_has_focus"] = bool(fix_text and "Focus:" in fix_text)

    passed_checks = sum(1 for passed in checks.values() if passed)
    total_checks = len(checks)
    pass_at_1 = round(passed_checks / total_checks, 3) if total_checks else 0.0

    required_checks = [
        "interim_instructions_present",
        "task_manifest_loaded",
        "task_prompts_count_matches_tasks",
        "all_task_prompts_present",
        "all_task_prompts_well_formed",
        "readme_exists",
        "eval_dir_exists",
        "score_log_exists",
        "trace_log_exists",
        "baseline_exists",
        "interim_report_exists",
        "report_exists",
        "requirements_summary_exists",
        "code_artifact_conversion_engine_exists",
        "code_artifact_evaluation_script_exists",
    ]
    status = "pass" if all(checks[name] for name in required_checks) else "fail"

    details: dict[str, Any] = {
        "checks": checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
    }
    if missing_task_prompts:
        details["missing_task_prompts"] = missing_task_prompts
    if malformed_task_prompts:
        details["malformed_task_prompts"] = malformed_task_prompts

    failed_required_checks = [name for name in required_checks if not checks.get(name, False)]
    if failed_required_checks:
        details["failed_required_checks"] = failed_required_checks

    return EvaluationResult(
        status=status,
        pass_at_1=pass_at_1,
        prompt_count=prompt_count,
        report_exists=report_exists,
        details=details,
    )


def write_output(path: Path, result: EvaluationResult) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        raise EvaluationError(f"Unable to write evaluation output: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args(argv)
    config = EvaluationConfig(project_root=args.project_root.resolve())

    try:
        result = evaluate(config)
        if args.output is not None:
            write_output(args.output.resolve(), result)

        LOGGER.info(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return 0 if result.status == "pass" else 1
    except EvaluationError as exc:
        LOGGER.error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())