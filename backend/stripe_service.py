# backend/stripe_service.py
"""
Stripe Checkout + webhook handling for subscriptions.

Flow:
  1. Frontend calls /billing/checkout -> we create a Checkout Session.
  2. User pays on Stripe-hosted page.
  3. Stripe fires webhooks -> we sync subscription state into Firestore.

If STRIPE_SECRET_KEY is unset the module operates in a disabled state and
endpoints return a clear error, so the rest of the app still runs locally.
"""
from __future__ import annotations
from typing import Optional, Dict, Any

from backend import config, billing

_stripe = None


def _client():
    global _stripe
    if _stripe is None:
        if not config.STRIPE_SECRET_KEY:
            raise RuntimeError("Stripe is not configured (STRIPE_SECRET_KEY missing)")
        import stripe

        stripe.api_key = config.STRIPE_SECRET_KEY
        _stripe = stripe
    return _stripe


def enabled() -> bool:
    return bool(config.STRIPE_SECRET_KEY)


def create_checkout_session(uid: str, email: str, plan_id: str) -> Dict[str, Any]:
    stripe = _client()
    plan = config.get_plan(plan_id)
    price_id = plan.get("stripe_price_id")
    if not price_id:
        raise RuntimeError(f"Plan '{plan_id}' has no Stripe price configured")

    # Reuse an existing customer if we have one.
    sub = billing.get_subscription(uid)
    customer_id = sub.get("stripe_customer_id")
    if not customer_id:
        customer = stripe.Customer.create(email=email, metadata={"uid": uid})
        customer_id = customer.id
        billing.set_subscription(uid, stripe_customer_id=customer_id)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{config.FRONTEND_URL}/billing?status=success",
        cancel_url=f"{config.FRONTEND_URL}/billing?status=cancel",
        metadata={"uid": uid, "plan_id": plan_id},
        subscription_data={"metadata": {"uid": uid, "plan_id": plan_id}},
    )
    return {"url": session.url, "id": session.id}


def create_portal_session(uid: str) -> Dict[str, Any]:
    stripe = _client()
    sub = billing.get_subscription(uid)
    customer_id = sub.get("stripe_customer_id")
    if not customer_id:
        raise RuntimeError("No Stripe customer for this user")
    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{config.FRONTEND_URL}/billing",
    )
    return {"url": portal.url}


def verify_and_parse_webhook(payload: bytes, sig_header: Optional[str]):
    stripe = _client()
    if not config.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET not set")
    return stripe.Webhook.construct_event(
        payload, sig_header, config.STRIPE_WEBHOOK_SECRET
    )


def handle_event(event: Dict[str, Any]) -> None:
    """Sync Firestore subscription state from a verified Stripe event."""
    etype = event.get("type", "")
    obj = event.get("data", {}).get("object", {})

    if etype == "checkout.session.completed":
        uid = (obj.get("metadata") or {}).get("uid")
        plan_id = (obj.get("metadata") or {}).get("plan_id")
        if uid:
            billing.set_subscription(
                uid,
                plan=plan_id or config.DEFAULT_PLAN,
                status="active",
                stripe_customer_id=obj.get("customer"),
                stripe_subscription_id=obj.get("subscription"),
            )

    elif etype in ("customer.subscription.updated", "customer.subscription.created"):
        uid = (obj.get("metadata") or {}).get("uid")
        if not uid:
            return
        items = (obj.get("items") or {}).get("data") or []
        price_id = items[0]["price"]["id"] if items else None
        billing.set_subscription(
            uid,
            plan=config.plan_id_from_price(price_id),
            status=obj.get("status", "active"),
            stripe_subscription_id=obj.get("id"),
            current_period_end=obj.get("current_period_end"),
        )

    elif etype == "customer.subscription.deleted":
        uid = (obj.get("metadata") or {}).get("uid")
        if uid:
            billing.set_subscription(uid, plan=config.DEFAULT_PLAN, status="canceled")
