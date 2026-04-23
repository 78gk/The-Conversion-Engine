from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProjectAdapter:
    root: Path

    def __post_init__(self) -> None:
        self.root = self.root.resolve()

    def resolve(self, relative_path: str) -> Path:
        path = (self.root / relative_path).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError(f"Path escapes project root: {relative_path}")
        return path

    def read_text(self, relative_path: str) -> str:
        path = self.resolve(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def write_text(self, relative_path: str, content: str) -> None:
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_text_if_changed(self, relative_path: str, content: str) -> bool:
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            existing = path.read_text(encoding="utf-8")
            if existing == content:
                return False

        path.write_text(content, encoding="utf-8")
        return True

    def read_json(self, relative_path: str, default: Any | None = None) -> Any:
        try:
            return json.loads(self.read_text(relative_path))
        except FileNotFoundError:
            if default is not None:
                return default
            raise

    def write_json(self, relative_path: str, data: Any) -> None:
        self.write_text(relative_path, json.dumps(data, indent=2, sort_keys=True))

    def write_json_if_changed(self, relative_path: str, data: Any) -> bool:
        return self.write_text_if_changed(relative_path, json.dumps(data, indent=2, sort_keys=True))

    def exists(self, relative_path: str) -> bool:
        return self.resolve(relative_path).exists()
