from typing import Literal

from pydantic import BaseModel, Field


class CreditCardTransaction(BaseModel):
    time: float = Field(ge=0)
    features: list[float] = Field(min_length=28, max_length=28)
    amount: float = Field(ge=0)


class PaySimTransaction(BaseModel):
    step: float = Field(ge=0)
    amount: float = Field(ge=0)
    old_balance_org: float = Field(ge=0)
    new_balance_orig: float = Field(ge=0)
    old_balance_dest: float = Field(ge=0)
    new_balance_dest: float = Field(ge=0)
    is_flagged_fraud: Literal[0, 1] = 0


class FraudPrediction(BaseModel):
    model_name: str
    model_version: str | None = None
    risk_score: float = Field(ge=0, le=1)
    is_fraud: bool
    threshold: float
