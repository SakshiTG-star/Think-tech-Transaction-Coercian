"""Explainable transaction coercion and scam-intent risk engine for SafePay AI.

This module uses transparent, rule-based heuristics designed for hackathon
demonstrations so judges can clearly trace how each behavioural and contextual
signal contributes to the final 0–100 risk score.

Core design principles:
1. No single anomaly (such as an unusual hour alone or a large amount alone)
   automatically flags high risk or fraud.
2. Risk escalates only when multiple coercion or scam-intent indicators combine.
3. The engine measures the presence of possible coercion indicators—it never
   claims to know the customer's intention with certainty.
"""

import re
from typing import Any, Dict, List, Optional


# Keywords commonly associated with scam pressure, urgency, or impersonation threats.
THREAT_COERCION_KEYWORDS = [
    "arrest",
    "police",
    "court",
    "warrant",
    "legal action",
    "threat",
    "blackmail",
    "freeze",
    "frozen",
    "blocked",
    "suspended",
    "deactivate",
    "penalty",
    "fine",
    "customs",
    "tax notice",
    "cyber cell",
    "cbi",
    "don't tell",
    "do not tell",
    "keep secret",
    "secret",
    "otp",
    "kyc expired",
    "account closed",
]

URGENCY_PRESSURE_KEYWORDS = [
    "urgent",
    "immediately",
    "right now",
    "asap",
    "hurry",
    "last chance",
    "within minutes",
    "deadline",
    "emergency",
    "forced",
    "pressure",
    "insisting",
    "caller said",
    "must pay now",
    "pay fast",
    "verify now",
]

REMOTE_ACCESS_KEYWORDS = [
    "remote",
    "anydesk",
    "teamviewer",
    "screen share",
    "screenshare",
    "screen-share",
    "quicksupport",
    "quick support",
    "rustdesk",
    "ultraviewer",
    "control my device",
    "sharing screen",
]


def get_engine_status() -> Dict[str, str]:
    """Return the current prototype status of the SafePay AI risk engine."""
    return {
        "engine_name": "SafePay Behaviour & Coercion Verifier",
        "mode": "Explainable Multi-Signal Engine Active",
        "stage": "Phase 2 — Coercion & Anomaly Analysis",
    }


def _extract_history_stats(
    customer_profile: Dict[str, Any],
    customer_history: Optional[Any],
) -> Dict[str, Any]:
    """Derive historical baseline statistics from transaction history or profile."""
    avg_amount = float(customer_profile.get("average_amount", 0.0) or 0.0)
    max_amount = 0.0
    familiar_payees: List[str] = list(customer_profile.get("familiar_payees", []))
    hours: List[int] = []

    # When a Pandas DataFrame (from get_customer_history) is provided, compute exact stats.
    if customer_history is not None and hasattr(customer_history, "empty") and not customer_history.empty:
        avg_amount = float(customer_history["amount"].mean())
        max_amount = float(customer_history["amount"].max())
        familiar_payees = sorted(customer_history["payee"].astype(str).unique().tolist())
        for raw_time in customer_history["time"].astype(str).tolist():
            match = re.match(r"^\s*(\d{1,2}):(\d{2})", raw_time)
            if match:
                hours.append(int(match.group(1)))

    # Fallback hour bounds if no DataFrame was supplied.
    if not hours:
        usual_text = str(customer_profile.get("usual_timing", ""))
        found_hours = re.findall(r"(\d{2}):\d{2}", usual_text)
        if len(found_hours) >= 2:
            hours = [int(found_hours[0]), int(found_hours[1])]
        else:
            hours = [9, 21]

    return {
        "avg_amount": round(avg_amount, 2),
        "max_amount": round(max_amount, 2),
        "familiar_payees": familiar_payees,
        "earliest_hour": min(hours),
        "latest_hour": max(hours),
    }


def _parse_hour(payment_time: Any) -> Optional[int]:
    """Extract the 0–23 hour from a 'HH:MM' string or datetime.time-like object."""
    if hasattr(payment_time, "hour"):
        return int(payment_time.hour)
    match = re.match(r"^\s*(\d{1,2}):(\d{2})", str(payment_time or ""))
    if match:
        hour = int(match.group(1))
        if 0 <= hour <= 23:
            return hour
    return None


def analyse_transaction(
    customer_profile: Dict[str, Any],
    payment_amount: float,
    payee: str,
    payment_time: Any,
    session_behaviour: str,
    payment_reason: str,
    customer_history: Optional[Any] = None,
) -> Dict[str, Any]:
    """Analyse a proposed transaction against customer baseline and coercion signals.

    Scoring logic (0–100 total, capped at 100):
    - Signal 1 (Amount vs. normal payments): up to +25 pts
    - Signal 2 (Familiar vs. new payee):     up to +18 pts
    - Signal 3 (Unusual transaction timing): up to +16 pts
    - Signal 4 (Hurried session):            up to +16 pts
    - Signal 5 (Remote-access hint):         up to +25 pts
    - Signal 6 (Urgency/threat in reason):   up to +24 pts

    Thresholds:
    - 0–34  -> Low    (Any single isolated anomaly stays Low so one signal alone
                       never falsely labels a legitimate transfer as high risk.)
    - 35–64 -> Medium (Two or more moderate indicators combined.)
    - 65–100 -> High  (Strong multi-signal coercion or scam-intent pattern.)
    """
    stats = _extract_history_stats(customer_profile, customer_history)
    score = 0
    reasons: List[str] = []
    positive_notes: List[str] = []

    amount_val = float(payment_amount or 0.0)
    payee_clean = str(payee or "").strip()
    time_str = (
        payment_time.strftime("%H:%M")
        if hasattr(payment_time, "strftime")
        else str(payment_time or "").strip()
    )
    session_lower = str(session_behaviour or "").strip().lower()
    reason_lower = str(payment_reason or "").strip().lower()

    # ------------------------------------------------------------------
    # Signal 1: Payment amount compared with normal historical payments
    # Max +25 pts so a large transfer by itself stays in the Low band.
    # ------------------------------------------------------------------
    avg_amount = stats["avg_amount"]
    max_amount = stats["max_amount"]
    if avg_amount > 0 and amount_val > 0:
        ratio = amount_val / avg_amount
        if ratio >= 3.0 and (max_amount == 0 or amount_val > max_amount * 1.15):
            score += 25
            reasons.append(
                f"Amount (₹{amount_val:,.2f}) is {ratio:.1f}x higher than the customer's "
                f"historical average (₹{avg_amount:,.2f}) and exceeds past maximums."
            )
        elif ratio >= 2.0:
            score += 16
            reasons.append(
                f"Amount (₹{amount_val:,.2f}) is {ratio:.1f}x higher than the customer's "
                f"usual average (₹{avg_amount:,.2f})."
            )
        elif ratio >= 1.5:
            score += 8
            reasons.append(
                f"Amount (₹{amount_val:,.2f}) is moderately above the historical average "
                f"(₹{avg_amount:,.2f})."
            )
        else:
            positive_notes.append(
                f"Payment amount (₹{amount_val:,.2f}) aligns with historical spending "
                f"(avg ₹{avg_amount:,.2f})."
            )

    # ------------------------------------------------------------------
    # Signal 2: Familiar or new payee
    # Max +18 pts. Unfamiliar payees raise caution but require other cues.
    # ------------------------------------------------------------------
    familiar_lower = [p.lower() for p in stats["familiar_payees"]]
    is_familiar = bool(payee_clean) and any(
        payee_clean.lower() == known or payee_clean.lower() in known or known in payee_clean.lower()
        for known in familiar_lower
    )

    if not payee_clean:
        score += 12
        reasons.append("No payee name was entered, making recipient familiarity unverifiable.")
    elif not is_familiar:
        score += 18
        reasons.append(
            f"'{payee_clean}' is a new payee not found in the customer's previous transaction history."
        )
    else:
        positive_notes.append(f"'{payee_clean}' matches a familiar payee from past transactions.")

    # ------------------------------------------------------------------
    # Signal 3: Unusual transaction timing
    # Max +16 pts so late-night/off-window timing alone never means fraud.
    # ------------------------------------------------------------------
    tx_hour = _parse_hour(payment_time)
    if tx_hour is not None:
        earliest = stats["earliest_hour"]
        latest = stats["latest_hour"]
        if tx_hour >= 22 or tx_hour < 6:
            score += 16
            reasons.append(
                f"Payment time ({time_str}) falls in late-night hours, outside the customer's "
                f"usual {earliest:02d}:00–{latest:02d}:59 pattern."
            )
        elif tx_hour < max(0, earliest - 1) or tx_hour > min(23, latest + 1):
            score += 10
            reasons.append(
                f"Payment time ({time_str}) is slightly outside the customer's normal "
                f"{earliest:02d}:00–{latest:02d}:59 activity window."
            )
        else:
            positive_notes.append(
                f"Payment time ({time_str}) fits within the customer's usual activity hours."
            )

    # ------------------------------------------------------------------
    # Signal 4: Hurried or erratic session behaviour
    # Max +16 pts. Captures rush/panic cues during payment initiation.
    # ------------------------------------------------------------------
    if any(word in session_lower for word in ["hurried", "rushed", "frantic", "fast"]):
        score += 16
        reasons.append(
            "Session behaviour indicates hurried or rushed navigation, which may reflect external pressure."
        )
    elif any(word in session_lower for word in ["hesitant", "repeated", "correction", "edits"]):
        score += 10
        reasons.append(
            "Session behaviour shows repeated edits or hesitation during transfer setup."
        )
    else:
        positive_notes.append("Session pacing appears calm without signs of rushing.")

    # ------------------------------------------------------------------
    # Signal 5: Remote-access hint (checked across session and reason text)
    # Max +25 pts. Strong indicator of guided scam / tech-support coercion.
    # ------------------------------------------------------------------
    combined_context = f"{session_lower} {reason_lower}"
    matched_remote = [kw for kw in REMOTE_ACCESS_KEYWORDS if kw in combined_context]
    if matched_remote:
        score += 25
        reasons.append(
            "Remote-access or screen-sharing indicator detected in session or payment context "
            f"(matched: {', '.join(sorted(set(matched_remote)))})."
        )

    # ------------------------------------------------------------------
    # Signal 6: Payment reason containing urgency, threats, or pressure
    # Max +24 pts. Looks for coercion language without assuming intent.
    # ------------------------------------------------------------------
    matched_threats = [kw for kw in THREAT_COERCION_KEYWORDS if kw in reason_lower]
    matched_urgency = [kw for kw in URGENCY_PRESSURE_KEYWORDS if kw in reason_lower]

    if matched_threats and (matched_urgency or len(matched_threats) >= 2):
        score += 24
        keywords_preview = ", ".join(sorted(set(matched_threats + matched_urgency))[:4])
        reasons.append(
            f"Payment reason contains combined threat/secrecy and urgency cues ({keywords_preview})."
        )
    elif matched_threats or len(matched_urgency) >= 2:
        score += 18
        keywords_preview = ", ".join(sorted(set(matched_threats + matched_urgency))[:3])
        reasons.append(
            f"Payment reason includes pressure or threat-related wording ({keywords_preview})."
        )
    elif matched_urgency:
        score += 10
        reasons.append(
            f"Payment reason mentions urgency ({matched_urgency[0]}), which warrants a brief check."
        )
    elif reason_lower:
        positive_notes.append("Payment reason text shows no obvious threat or pressure keywords.")

    # Cap total score cleanly between 0 and 100.
    final_score = max(0, min(100, int(round(score))))

    # Combine risk reasons first; if none or Low, add baseline alignment notes.
    if not reasons:
        reasons = positive_notes or [
            "Transaction parameters remain consistent with the customer's historical baseline."
        ]
    elif final_score < 35 and positive_notes:
        reasons.append(positive_notes[0])

    # Classify into Low / Medium / High and provide calm, non-accusatory guidance.
    if final_score < 35:
        risk_category = "Low"
        recommended_action = (
            "Low coercion indicators observed. Standard confirmation is appropriate—"
            "double-check payee details and proceed normally if you initiated this transfer freely."
        )
    elif final_score < 65:
        risk_category = "Medium"
        recommended_action = (
            "Moderate anomaly signals detected. Pause for 60 seconds, verify the recipient "
            "through an independent trusted number, and confirm nobody is rushing you."
        )
    else:
        risk_category = "High"
        recommended_action = (
            "Multiple potential coercion indicators detected. Hold the transfer temporarily, "
            "disconnect any active phone call or screen-sharing session, and verify independently "
            "with family or your bank's official helpline."
        )

    return {
        "risk_score": final_score,
        "risk_category": risk_category,
        "reasons": reasons,
        "recommended_action": recommended_action,
        "baseline_comparison": {
            "customer_name": customer_profile.get("customer_name", "Unknown"),
            "historical_average": avg_amount,
            "historical_max": max_amount,
            "is_familiar_payee": is_familiar,
            "usual_timing": customer_profile.get("usual_timing", "N/A"),
            "payment_time": time_str,
        },
    }
