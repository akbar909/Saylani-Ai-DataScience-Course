class ForecastModel:
    """Contract for a future LSTM or classical forecasting implementation."""

    def fit(self, values: list[float]) -> None:
        if len(values) < 2:
            raise ValueError("At least two observations are required")

    def predict(self, horizon_days: int) -> list[float]:
        if horizon_days < 1:
            raise ValueError("horizon_days must be positive")
        raise RuntimeError("Forecasting artifact is not trained yet")
