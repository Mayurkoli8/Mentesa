# backend/payment_service.py
"""
Dodo Payments integration (Merchant of Record) for subscriptions.

Flow:
  1. Frontend calls /billing/checkout -> we create a Dodo Checkout Session
     for the chosen plan's product and redirect the user to checkout_url.
  2. User pays on Dodo's hosted checkout.
  3. Dodo fires Standard Webhooks -> we verify and sync subscription state
     into Firestore.

If DODO_PAYMENTS_API_KEY is unset the module is disabled and billing
endpoints return a clear error, so the rest of the app still runs locally.
"""
from __future__ import annotations
from typing import Optional, Dict, Any

from backend import config, billing

_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.DODO_API_KEY:
            raise RuntimeError("Dodo Payments is not configured (DODO_PAYMENTS_API_KEY missing)")
        from dodopayments import DodoPayments

        _client = DodoPayments(
            bearer_token=config.DODO_API_KEY,
            environment=config.DODO_ENVIRONMENT,
        )
    return _client


def enabled() -> bool:
    return bool(config.DODO_API_KEY)


def create_checkout_session(uid: str, email: str, name: str, plan_id: str) -> Dict[str, Any]:
    client = _get_client()
    plan = config.get_plan(plan_id)
    product_id = plan.get("product_id")
    if not product_id:
        raise RuntimeError(f"Plan '{plan_id}' has no Dodo product configured")

    # Reuse an existing Dodo customer if we have one stored.
    sub = billing.get_subscription(uid)
    customer_id = sub.get("dodo_customer_id")

    if customer_id:
        customer_param: Dict[str, Any] = {"customer_id": customer_id}
    else:
        customer_param = {"email": email, "name": name or email.split("@")[0]}

    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer=customer_param,
        return_url=f"{config.FRONTEND_URL}/billing?status=success",
        metadata={"uid": uid, "plan_id": plan_id},
        subscription_data={"metadata": {"uid": uid, "plan_id": plan_id}},
    )
    return {"url": session.checkout_url, "id": session.session_id}


def create_portal_session(uid: str) -> Dict[str, Any]:
    client = _get_client()
    sub = billing.get_subscription(uid)
    customer_id = sub.get("dodo_customer_id")
    if not customer_id:
        raise RuntimeError("No Dodo customer for this user yet")
    portal = client.customers.customer_portal.create(
        customer_id=customer_id,
        return_url=f"{config.FRONTEND_URL}/billing",
    )
    return {"url": portal.link}


def verify_and_parse_webhook(payload: bytes, headers: Dict[str, str]):
    """Verify a Standard Webhooks signature and return the parsed event."""
    client = _get_client()
    if not config.DODO_WEBHOOK_KEY:
        raise RuntimeError("DODO_PAYMENTS_WEBHOOK_KEY not set")
    body = payload.decode("utf-8") if isinstance(payload, (bytes, bytearray)) else payload
    return client.webhooks.unwrap(
        body,
        headers={
            "webhook-id": headers.get("webhook-id", ""),
            "webhook-signature": headers.get("webhook-signature", ""),
            "webhook-timestamp": headers.get("webhook-timestamp", ""),
        },
        key=config.DODO_WEBHOOK_KEY,
    )


def _extract(obj: Any, key: str, default=None):
    """Read a field whether the payload is a dict or an SDK model."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def handle_event(event: Any) -> None:
    """Sync Firestore subscription state from a verified Dodo event.

    Subscription lifecycle events (Standard Webhooks payload):
      subscription.active / .renewed  -> active
      subscription.on_hold            -> past_due
      subscription.cancelled/.expired/.failed -> downgrade to free
    """
    etype = _extract(event, "type", "") or ""
    data = _extract(event, "data", {}) or {}
    metadata = _extract(data, "metadata", {}) or {}
    uid = metadata.get("uid")
    product_id = _extract(data, "product_id")
    customer = _extract(data, "customer", {}) or {}
    customer_id = _extract(customer, "customer_id") or _extract(data, "customer_id")
    subscription_id = _extract(data, "subscription_id")
    next_billing = _extract(data, "next_billing_date")

    if not uid:
        # Without our uid metadata we can't attribute the subscription.
        print(f"[Dodo] event {etype} without uid metadata; skipping")
        return

    if etype in ("subscription.active", "subscription.renewed"):
        plan_id = metadata.get("plan_id") or config.plan_id_from_product(product_id)
        billing.set_subscription(
            uid,
            plan=plan_id,
            status="active",
            dodo_customer_id=customer_id,
            dodo_subscription_id=subscription_id,
            current_period_end=next_billing,
        )

    elif etype == "subscription.on_hold":
        billing.set_subscription(uid, status="past_due")

    elif etype in ("subscription.cancelled", "subscription.expired", "subscription.failed"):
        billing.set_subscription(uid, plan=config.DEFAULT_PLAN, status="canceled")

    elif etype == "subscription.plan_changed":
        plan_id = metadata.get("plan_id") or config.plan_id_from_product(product_id)
        billing.set_subscription(uid, plan=plan_id, status="active")
