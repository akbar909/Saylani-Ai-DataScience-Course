from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.core.config import Settings, get_settings


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
    settings: Settings = Depends(get_settings),
) -> dict[str, object]:
    payload = await request.body()
    
    if not settings.stripe_webhook_secret.strip():
        return {
            "received": bool(payload),
            "processed": True,
            "status": "simulated_success",
            "reason": "Stripe webhook received in demo mode (signing secret not set)",
        }
        
    try:
        # pyrefly: ignore [missing-import]
        import stripe
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Webhook Error: {str(error)}")

    event_type = event.get("type", "")
    
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        # Handle active subscription creation
        return {"received": True, "processed": True, "event": event_type, "customer": session.get("customer")}
    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        return {"received": True, "processed": True, "event": event_type}

    return {"received": True, "processed": True, "event": event_type}

