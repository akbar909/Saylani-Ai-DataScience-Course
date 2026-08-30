from pathlib import Path


class AutoencoderFraudDetector:
    """Optional extension point for the Phase 6 unsupervised detector."""

    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path

    def predict_score(self, values: list[float]) -> float:
        raise RuntimeError("Autoencoder artifact is not trained; use the supervised baseline for inference")
