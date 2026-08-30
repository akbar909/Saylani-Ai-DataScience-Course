import sys
from pathlib import Path
from uuid import uuid4

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def create_test_user(client: TestClient, password: str = "password123") -> str:
    email = f"test+{uuid4().hex}@example.com"
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "organization_name": "Test Org"},
    )
    assert signup_response.status_code == 201
    token = signup_response.json()["access_token"]
    return token


def login_test_user(client: TestClient, email: str = "test@example.com", password: str = "password123") -> str:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_health_reports_loaded_models() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/models")

    assert response.status_code == 200
    body = response.json()
    assert body["creditcard_baseline"]["available"] is True
    assert body["paysim_baseline"]["available"] is True


def test_fraud_prediction_routes_return_scores() -> None:
    with TestClient(app) as client:
        token = create_test_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        credit_response = client.post(
            "/api/v1/fraud/credit-card/predict",
            json={"time": 0, "features": [0.0] * 28, "amount": 10.0},
            headers=headers,
        )
        paysim_response = client.post(
            "/api/v1/fraud/paysim/predict",
            json={
                "step": 1,
                "amount": 100.0,
                "old_balance_org": 1000.0,
                "new_balance_orig": 900.0,
                "old_balance_dest": 0.0,
                "new_balance_dest": 100.0,
                "is_flagged_fraud": 0,
            },
            headers=headers,
        )

    assert credit_response.status_code == 200
    assert paysim_response.status_code == 200
    assert 0 <= credit_response.json()["risk_score"] <= 1
    assert 0 <= paysim_response.json()["risk_score"] <= 1


def test_forecast_readiness_route() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/forecasts/readiness")

    assert response.status_code == 200
    body = response.json()
    assert "available" in body and "message" in body


def test_billing_status_route() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/billing/status")

    assert response.status_code == 200
    body = response.json()
    assert body["plan"] == "starter"
    assert body["status"] == "active"
    assert body["stripe_configured"] is False
