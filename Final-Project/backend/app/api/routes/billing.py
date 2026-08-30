from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.config import Settings, get_settings


router = APIRouter(prefix="/billing", tags=["billing"])


class BillingStatus(BaseModel):
    plan: str
    status: str
    stripe_configured: bool


class CheckoutRequest(BaseModel):
    plan: str = "pro"


class SessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    demo_mode: bool


@router.get("/status", response_model=BillingStatus)
def billing_status(settings: Settings = Depends(get_settings)) -> BillingStatus:
    stripe_configured = bool(settings.stripe_secret_key.strip())
    return BillingStatus(
        plan="starter",
        status="active",
        stripe_configured=stripe_configured,
    )


@router.post("/create-checkout-session", response_model=SessionResponse)
def create_checkout_session(
    req: CheckoutRequest, settings: Settings = Depends(get_settings)
) -> SessionResponse:
    if settings.stripe_secret_key.strip():
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": settings.stripe_price_id_pro or "price_pro_monthly",
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{settings.frontend_origin}/billing?success=true",
                cancel_url=f"{settings.frontend_origin}/billing?canceled=true",
            )
            return SessionResponse(checkout_url=session.url, session_id=session.id, demo_mode=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
    # Fallback demo mode url
    return SessionResponse(
        checkout_url=f"{settings.frontend_origin}/billing?checkout=demo_success&plan={req.plan}",
        session_id="demo_session_12345",
        demo_mode=True,
    )


@router.post("/create-portal-session", response_model=SessionResponse)
def create_portal_session(settings: Settings = Depends(get_settings)) -> SessionResponse:
    if settings.stripe_secret_key.strip():
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key
            # Demo customer ID or dynamic
            session = stripe.billing_portal.Session.create(
                customer="cus_demo123",
                return_url=f"{settings.frontend_origin}/billing",
            )
            return SessionResponse(checkout_url=session.url, session_id=session.id, demo_mode=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Stripe portal error: {str(e)}")

    return SessionResponse(
        checkout_url=f"{settings.frontend_origin}/billing?portal=demo",
        session_id="demo_portal_12345",
        demo_mode=True,
    )

