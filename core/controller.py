from __future__ import annotations

from pathlib import Path

from core.project_adapter import ProjectAdapter
from core.router import Router


class ControllerError(RuntimeError):
    pass


class Controller:
    valid_phases = {"planning", "building", "evaluating", "debugging", "improving", "reporting"}

    def __init__(self):
        self.adapter = ProjectAdapter(Path(__file__).resolve().parents[1])
        self.router = Router(self.adapter)
        self.state = self.load_state()

    def load_state(self):
        state = self.adapter.read_json("memory/state.json", default={"phase": "planning"})
        if not isinstance(state, dict):
            raise ControllerError("memory/state.json must contain an object")

        phase = state.get("phase", "planning")
        if phase == "reporting":
            return {"phase": "planning"}
        if phase not in self.valid_phases:
            raise ControllerError(f"Unknown phase: {phase}")

        return {"phase": phase}

    def save_state(self):
        self.adapter.write_json("memory/state.json", self.state)

    def run(self):
        def dispatch_or_raise(phase: str):
            result = self.router.dispatch({"phase": phase})
            if result.get("status") == "error":
                raise ControllerError(result.get("message", "Unknown controller error"))
            return result

        phase = self.state.get("phase", "planning")
        if phase not in self.valid_phases:
            raise ControllerError(f"Unsupported phase: {phase}")

        if phase in {"planning", "building", "evaluating"}:
            dispatch_or_raise("planning")
            self.state["phase"] = "building"
            self.save_state()

            dispatch_or_raise("building")
            self.state["phase"] = "evaluating"
            self.save_state()

            eval_result = dispatch_or_raise("evaluating")
            if eval_result.get("status") == "fail":
                self.state["phase"] = "debugging"
                self.save_state()

                dispatch_or_raise("debugging")
                self.state["phase"] = "reporting"
                self.save_state()

                report_result = dispatch_or_raise("reporting")
                self.state["phase"] = "planning"
                self.save_state()
                return {"status": "fail", "evaluation": eval_result, "reporting": report_result}

            self.state["phase"] = "improving"
            self.save_state()

            dispatch_or_raise("improving")
            self.state["phase"] = "reporting"
            self.save_state()

            report_result = dispatch_or_raise("reporting")
            self.state["phase"] = "planning"
            self.save_state()
            return {"status": "pass", "evaluation": eval_result, "reporting": report_result}

        if phase == "debugging":
            dispatch_or_raise("debugging")
            self.state["phase"] = "reporting"
            self.save_state()

            report_result = dispatch_or_raise("reporting")
            self.state["phase"] = "planning"
            self.save_state()
            return {"status": "fail", "reporting": report_result}

        if phase == "improving":
            dispatch_or_raise("improving")
            self.state["phase"] = "reporting"
            self.save_state()

            report_result = dispatch_or_raise("reporting")
            self.state["phase"] = "planning"
            self.save_state()
            return {"status": "pass", "reporting": report_result}

        if phase == "reporting":
            report_result = dispatch_or_raise("reporting")
            self.state["phase"] = "planning"
            self.save_state()
            return report_result

        raise ControllerError(f"Unsupported phase: {phase}")
