from collections.abc import Sequence

from app.core.model_registry import ModelRegistry
from app.ml.preprocessing import as_feature_frame


def detect_fraud(registry: ModelRegistry, artifact_name: str, values: Sequence[float]) -> dict[str, float | bool]:
    artifact = registry.load(artifact_name)
    frame = as_feature_frame(values, artifact.metrics["feature_columns"])
    score = float(artifact.model.predict_proba(frame)[0][1])
    return {"risk_score": score, "is_fraud": score >= 0.5}
