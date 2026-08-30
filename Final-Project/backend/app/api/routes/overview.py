import csv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

from app.core.config import PROJECT_ROOT
from app.core.model_registry import ModelRegistry
from app.models.anomaly import Anomaly
from app.models.transaction import Transaction


router = APIRouter(prefix="/overview", tags=["overview"])


def _load_sample_transactions(limit: int = 5) -> list[dict[str, str]]:
    source_path = PROJECT_ROOT / "creditcard.csv"
    if not source_path.exists():
        return []
    transactions: list[dict[str, str]] = []
    with source_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for index, row in enumerate(reader):
            if index >= limit:
                break
            transactions.append(
                {
                    "time": row.get("Time", ""),
                    "amount": row.get("Amount", ""),
                    "class": row.get("Class", ""),
                }
            )
    return transactions


@router.get("")
async def overview(request: Request) -> dict[str, Any]:
    registry: ModelRegistry = request.app.state.model_registry
    try:
        credit = registry.load("creditcard_baseline").metrics
    except (FileNotFoundError, OSError):
        credit = {}
    try:
        paysim = registry.load("paysim_baseline").metrics
    except (FileNotFoundError, OSError):
        paysim = {}

    transactions = []
    signals = []
    if hasattr(request.app.state, "database_client"):
        try:
            transactions = [
                {
                    "amount": f"{transaction.amount:.2f}",
                    "currency": transaction.currency,
                    "category": transaction.category,
                    "description": transaction.description,
                    "date": transaction.transaction_date.isoformat(),
                }
                for transaction in await Transaction.find().sort("-transaction_date").limit(5).to_list()
            ]
            signals = [
                {
                    "title": f"{anomaly.severity.title()} anomaly",
                    "description": anomaly.reason,
                }
                for anomaly in await Anomaly.find().sort("-created_at").limit(3).to_list()
            ]
        except Exception:
            transactions = []
            signals = []

    if not transactions:
        transactions = _load_sample_transactions()

    return {
        "models": {
            "creditcard": {
                "available": bool(credit),
                "precision": credit.get("precision"),
                "recall": credit.get("recall"),
                "pr_auc": credit.get("pr_auc"),
                "roc_auc": credit.get("roc_auc"),
            },
            "paysim": {
                "available": bool(paysim),
                "precision": paysim.get("precision"),
                "recall": paysim.get("recall"),
                "pr_auc": paysim.get("pr_auc"),
                "roc_auc": paysim.get("roc_auc"),
            },
        },
        "transactions": transactions,
        "signals": signals,
        "data_source": "trained model artifacts",
    }
