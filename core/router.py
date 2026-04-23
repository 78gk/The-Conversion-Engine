from __future__ import annotations

from typing import Any, Callable, Dict

from agent import builder, debugger, evaluator, improver, planner, reporter
from core.project_adapter import ProjectAdapter


class Router:
    def __init__(self, adapter: ProjectAdapter) -> None:
        self.adapter = adapter
        self._handlers: Dict[str, Callable[[], Dict[str, Any] | None]] = {
            "planning": lambda: planner.run(self.adapter),
            "building": lambda: builder.run(self.adapter),
            "evaluating": lambda: evaluator.run(self.adapter),
            "debugging": lambda: debugger.run(self.adapter),
            "improving": lambda: improver.run(self.adapter),
            "reporting": lambda: reporter.run(self.adapter),
        }

    def dispatch(self, task: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = task.get("agent") or task.get("phase")
        handler = self._handlers.get(agent_name)
        if handler is None:
            return {"status": "error", "message": f"Unknown agent: {agent_name}"}

        try:
            result = handler()
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

        if result is None:
            return {"status": "success"}
        return result
