from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_fraud_service
from app.models.user import User
from app.schemas.fraud import CreditCardTransaction, FraudPrediction, PaySimTransaction
from app.services.fraud import FraudService


router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.post("/credit-card/predict", response_model=FraudPrediction)
def predict_credit_card(
    transaction: CreditCardTransaction,
    service: FraudService = Depends(get_fraud_service),
    current_user: User = Depends(get_current_user),
) -> FraudPrediction:
    values = [transaction.time, *transaction.features, transaction.amount]
    return service.predict("creditcard_baseline", values)


@router.post("/paysim/predict", response_model=FraudPrediction)
def predict_paysim(
    transaction: PaySimTransaction,
    service: FraudService = Depends(get_fraud_service),
    current_user: User = Depends(get_current_user),
) -> FraudPrediction:
    values = [
        transaction.step,
        transaction.amount,
        transaction.old_balance_org,
        transaction.new_balance_orig,
        transaction.old_balance_dest,
        transaction.new_balance_dest,
        transaction.is_flagged_fraud,
    ]
    return service.predict("paysim_baseline", values)
