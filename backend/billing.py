# backend/billing.py
"""
Subscription + usage metering, stored in Firestore.

Documents:
  subscriptions/{uid}  -> { plan, status, stripe_customer_id,
                            stripe_subscription_id, current_period_end }
  usage/{uid}_{YYYYMM} -> { uid, period, message_count }

Limits are enforced by main.py before each chat / bot creation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional

from utils.firebase_config import db
from firebase_admin import firestore as fa_firestore
from backend import config


def _period_key(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.utcnow()
    return dt.strftime("%Y%m")


# -------------------------------------------------
# Subscriptions
# -------------------------------------------------
def get_subscription(uid: str) -> Dict[str, Any]:
    """Return the user's subscription doc, defaulting to the free plan."""
    if not uid:
        return {"plan": config.DEFAULT_PLAN, "status": "active"}
    doc = db.collection("subscriptions").document(uid).get()
    if not doc.exists:
        return {"plan": config.DEFAULT_PLAN, "status": "active"}
    data = doc.to_dict() or {}
    data.setdefault("plan", config.DEFAULT_PLAN)
    data.setdefault("status", "active")
    return data


def set_subscription(uid: str, **fields) -> None:
    fields["updated_at"] = datetime.utcnow().isoformat()
    db.collection("subscriptions").document(uid).set(fields, merge=True)


def current_plan(uid: str) -> Dict[str, Any]:
    """Return the resolved plan definition for a user."""
    sub = get_subscription(uid)
    plan = config.get_plan(sub.get("plan"))
    # If subscription is not active, fall back to free limits.
    if sub.get("status") not in ("active", "trialing", None):
        plan = config.get_plan(config.DEFAULT_PLAN)
    return plan


# -------------------------------------------------
# Usage metering
# -------------------------------------------------
def get_usage(uid: str) -> int:
    if not uid:
        return 0
    key = f"{uid}_{_period_key()}"
    doc = db.collection("usage").document(key).get()
    if not doc.exists:
        return 0
    return int((doc.to_dict() or {}).get("message_count", 0))


def increment_usage(uid: str, amount: int = 1) -> int:
    """Atomically increment this period's message count; returns new total."""
    if not uid:
        return 0
    key = f"{uid}_{_period_key()}"
    ref = db.collection("usage").document(key)
    ref.set(
        {
            "uid": uid,
            "period": _period_key(),
            "message_count": fa_firestore.Increment(amount),
            "updated_at": datetime.utcnow().isoformat(),
        },
        merge=True,
    )
    return get_usage(uid)


def can_send_message(uid: str) -> Dict[str, Any]:
    """Check whether the user is within their monthly message allowance."""
    plan = current_plan(uid)
    used = get_usage(uid)
    limit = plan["message_limit"]
    return {
        "allowed": used < limit,
        "used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "plan": plan["name"],
    }


def can_create_bot(uid: str, current_bot_count: int) -> Dict[str, Any]:
    plan = current_plan(uid)
    limit = plan["bot_limit"]
    allowed = (limit is None) or (current_bot_count < limit)
    return {
        "allowed": allowed,
        "current": current_bot_count,
        "limit": limit,
        "plan": plan["name"],
    }


def usage_summary(uid: str) -> Dict[str, Any]:
    sub = get_subscription(uid)
    plan = current_plan(uid)
    used = get_usage(uid)
    return {
        "plan_id": sub.get("plan", config.DEFAULT_PLAN),
        "plan_name": plan["name"],
        "status": sub.get("status", "active"),
        "message_used": used,
        "message_limit": plan["message_limit"],
        "bot_limit": plan["bot_limit"],
        "branding": plan["branding"],
        "current_period_end": sub.get("current_period_end"),
    }
