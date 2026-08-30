from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    metric: str = Field(default="revenue", pattern="^(revenue|expenses|churn)$")
    horizon_days: int = Field(default=30, ge=1, le=365)


class ForecastReadiness(BaseModel):
    available: bool
    message: str


class ForecastPoint(BaseModel):
    date: str
    predicted: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    metric: str
    horizon_days: int
    data: list[ForecastPoint]
    summary: dict[str, float]

