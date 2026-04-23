"""Production-ready build system for the Conversion Engine task flow.

This module reads the task manifest from memory, generates prompt artifacts,
and writes a concise build summary. It is intentionally small and defensive:
inputs are validated, filesystem failures are surfaced with clear exceptions,
and the implementation avoids hidden side effects.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)

REQUIREMENTS: tuple[str, ...] = (
    "production ready code",
    "proper structure",
    "include error handling",
)
DO_NOT: tuple[str, ...] = (
    "add unnecessary features",
)


class BuildSystemError(RuntimeError):
    """Base error for build failures."""


class TaskManifestError(BuildSystemError):
    """Raised when the task manifest cannot be loaded or validated."""


class ArtifactWriteError(BuildSystemError):
    """Raised when an artifact cannot be written safely."""


@dataclass(frozen=True)
class TaskSpec:
    """Validated task input from the manifest."""

    task: str
    tool: str | None = None


@dataclass
class BuildSummary:
    """Structured result from a build run."""

    task_count: int = 0
    prompt_files: list[Path] = field(default_factory=list)
    report_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_count": self.task_count,
            "prompt_files": [str(path) for path in self.prompt_files],
            "report_path": str(self.report_path) if self.report_path else None,
        }


class ConversionEngineBuildSystem:
    """Generate prompt artifacts and a small build report."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path(__file__).resolve().parents[2]).resolve()
        self.memory_dir = self.root / "memory"
        self.prompt_dir = self.root / "artifacts" / "prompts"
        self.report_dir = self.root / "artifacts" / "reports"

    def build(self) -> BuildSummary:
        tasks = self._load_tasks()
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        summary = BuildSummary(task_count=len(tasks))
        for index, task in enumerate(tasks):
            prompt_path = self.prompt_dir / f"task_{index}.txt"
            prompt_text = self._render_prompt(task)
            self._write_text(prompt_path, prompt_text)
            summary.prompt_files.append(prompt_path)

        report_path = self.report_dir / "README.md"
        self._write_text(report_path, self._render_report(summary))
        summary.report_path = report_path
        return summary

    def _load_tasks(self) -> list[TaskSpec]:
        manifest_path = self.memory_dir / "tasks.json"
        if not manifest_path.exists():
            raise TaskManifestError(f"Task manifest not found: {manifest_path}")

        try:
            raw_tasks = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise TaskManifestError(f"Invalid JSON in task manifest: {manifest_path}") from exc
        except OSError as exc:
            raise TaskManifestError(f"Unable to read task manifest: {manifest_path}") from exc

        if not isinstance(raw_tasks, list):
            raise TaskManifestError("Task manifest must contain a JSON list.")

        tasks: list[TaskSpec] = []
        for index, item in enumerate(raw_tasks):
            if not isinstance(item, dict):
                raise TaskManifestError(f"Task entry {index} must be an object.")

            task_text = item.get("task")
            if not isinstance(task_text, str) or not task_text.strip():
                raise TaskManifestError(f"Task entry {index} is missing a valid 'task' field.")

            tool_value = item.get("tool")
            tool = tool_value if isinstance(tool_value, str) and tool_value.strip() else None
            tasks.append(TaskSpec(task=task_text.strip(), tool=tool))

        return tasks

    def _render_prompt(self, task: TaskSpec) -> str:
        lines = [f"Task: {task.task}", "", "Requirements:"]
        lines.extend(f"- {requirement}" for requirement in REQUIREMENTS)
        lines.extend(("", "DO NOT:"))
        lines.extend(f"- {item}" for item in DO_NOT)
        return "\n".join(lines) + "\n"

    def _render_report(self, summary: BuildSummary) -> str:
        prompt_list = "\n".join(f"- {path.name}" for path in summary.prompt_files) or "- none"
        return (
            "# Build Report\n\n"
            f"- Tasks processed: {summary.task_count}\n"
            f"- Prompt artifacts:\n{prompt_list}\n"
        )

    def _write_text(self, path: Path, content: str) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise ArtifactWriteError(f"Unable to write artifact: {path}") from exc


def run() -> BuildSummary:
    """Convenience wrapper used by the rest of the workspace."""

    return ConversionEngineBuildSystem().build()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    summary = run()
    LOGGER.info("Build complete: %s", summary.to_dict())


if __name__ == "__main__":
    main()
