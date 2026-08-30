from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import joblib

from app.core.config import Settings


@dataclass(frozen=True)
class ModelArtifact:
    name: str
    model: Any
    metrics: dict[str, Any]


class ModelRegistry:
    def __init__(self, settings: Settings) -> None:
        self._root = Path(settings.model_artifact_root).resolve()
        self._artifacts: dict[str, ModelArtifact] = {}

    def load(self, name: str) -> ModelArtifact:
        if name in self._artifacts:
            return self._artifacts[name]
        artifact_dir = self._root / name
        model_path = artifact_dir / "model.joblib"
        metrics_path = artifact_dir / "metrics.json"
        if not model_path.is_file() or not metrics_path.is_file():
            raise FileNotFoundError(f"Model artifact is incomplete: {artifact_dir}")
        artifact = ModelArtifact(
            name=name,
            model=joblib.load(model_path),
            metrics=json.loads(metrics_path.read_text(encoding="utf-8")),
        )
        self._artifacts[name] = artifact
        return artifact

    def status(self, name: str) -> dict[str, Any]:
        try:
            artifact = self.load(name)
        except (FileNotFoundError, OSError, ValueError) as error:
            return {"available": False, "error": str(error)}
        return {
            "available": True,
            "model_name": artifact.metrics.get("model_name"),
            "model_version": artifact.metrics.get("model_version"),
        }
