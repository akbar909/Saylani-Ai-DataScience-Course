from collections.abc import Sequence


def predict_forecast(values: Sequence[float], horizon_days: int) -> list[float]:
    if not values:
        raise ValueError("values cannot be empty")
    if horizon_days < 1:
        raise ValueError("horizon_days must be positive")
    raise RuntimeError("Forecasting artifact is not trained yet")
