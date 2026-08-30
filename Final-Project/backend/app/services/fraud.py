from collections.abc import Sequence

import pandas as pd

from app.core.model_registry import ModelRegistry
from app.schemas.fraud import FraudPrediction


class FraudService:
    def __init__(self, registry: ModelRegistry) -> None:
        self._registry = registry

    def predict(self, artifact_name: str, values: Sequence[float]) -> FraudPrediction:
        artifact = self._registry.load(artifact_name)
        feature_columns = artifact.metrics["feature_columns"]
        frame = pd.DataFrame([list(values)], columns=feature_columns)
        probability = float(artifact.model.predict_proba(frame)[0][1])
        return FraudPrediction(
            model_name=str(artifact.metrics.get("model_name", artifact_name)),
            model_version=artifact.metrics.get("model_version"),
            risk_score=probability,
            is_fraud=probability >= 0.5,
            threshold=0.5,
        )
