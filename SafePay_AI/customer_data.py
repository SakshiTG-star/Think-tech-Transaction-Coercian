"""Synthetic customer profiles and transaction history for SafePay AI.

All records in this module are 100% fictional and created solely for
demonstrating behaviour-based transaction verification in a hackathon prototype.
No real bank accounts, live feeds, or payment APIs are used.
"""

from typing import Any, Dict, List
import pandas as pd


# Three fictional customer profiles with synthetic past transactions.
CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "Aarav Sharma": {
        "customer_id": "CUST-SYN-001",
        "segment": "Salaried Software Engineer",
        "normal_behaviour": (
            "Usually transfers modest amounts between ₹500 and ₹8,500 during "
            "daytime and evening hours (09:00–21:00) to recurring utility providers, "
            "groceries, rent, and known family contacts."
        ),
        "transactions": [
            {
                "date": "2026-11-02",
                "time": "10:15",
                "payee": "FreshMart Groceries",
                "category": "Groceries",
                "amount": 1850.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-05",
                "time": "19:40",
                "payee": "Metro Power Utility",
                "category": "Utilities",
                "amount": 2420.00,
                "channel": "NetBanking",
            },
            {
                "date": "2026-11-09",
                "time": "13:20",
                "payee": "Priya Sharma (Sister)",
                "category": "Family Transfer",
                "amount": 5000.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-14",
                "time": "18:05",
                "payee": "FreshMart Groceries",
                "category": "Groceries",
                "amount": 1340.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-18",
                "time": "11:30",
                "payee": "City Fiber Broadband",
                "category": "Utilities",
                "amount": 1199.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-21",
                "time": "20:10",
                "payee": "Priya Sharma (Sister)",
                "category": "Family Transfer",
                "amount": 3200.00,
                "channel": "UPI",
            },
        ],
    },
    "Meera Nair": {
        "customer_id": "CUST-SYN-002",
        "segment": "Retired School Principal",
        "normal_behaviour": (
            "Prefers low-risk, predictable daytime payments (08:30–16:30) under "
            "₹4,000, mainly to local pharmacies, pension-linked bills, and her son."
        ),
        "transactions": [
            {
                "date": "2026-11-01",
                "time": "09:10",
                "payee": "CarePlus Pharmacy",
                "category": "Healthcare",
                "amount": 960.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-04",
                "time": "11:45",
                "payee": "GreenLeaf Organics",
                "category": "Groceries",
                "amount": 1120.00,
                "channel": "Debit Card",
            },
            {
                "date": "2026-11-10",
                "time": "10:00",
                "payee": "Rohan Nair (Son)",
                "category": "Family Transfer",
                "amount": 3500.00,
                "channel": "Bank Transfer",
            },
            {
                "date": "2026-11-15",
                "time": "14:25",
                "payee": "CarePlus Pharmacy",
                "category": "Healthcare",
                "amount": 780.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-20",
                "time": "15:50",
                "payee": "Sunrise Water & Gas",
                "category": "Utilities",
                "amount": 1450.00,
                "channel": "NetBanking",
            },
        ],
    },
    "Vikram Desai": {
        "customer_id": "CUST-SYN-003",
        "segment": "Independent Design Consultant",
        "normal_behaviour": (
            "Regularly pays software subscriptions, studio vendors, and coworking "
            "invoices between ₹2,000 and ₹18,000 during business hours (10:00–19:00)."
        ),
        "transactions": [
            {
                "date": "2026-11-03",
                "time": "10:30",
                "payee": "CloudCanvas Suite",
                "category": "Software Subscription",
                "amount": 4200.00,
                "channel": "Corporate Card",
            },
            {
                "date": "2026-11-06",
                "time": "15:15",
                "payee": "WorkHub Coworking",
                "category": "Workspace Rent",
                "amount": 12500.00,
                "channel": "NEFT",
            },
            {
                "date": "2026-11-11",
                "time": "12:40",
                "payee": "PixelPrint Studio",
                "category": "Vendor Payment",
                "amount": 6800.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-14",
                "time": "17:20",
                "payee": "CloudCanvas Suite",
                "category": "Software Subscription",
                "amount": 4200.00,
                "channel": "Corporate Card",
            },
            {
                "date": "2026-11-17",
                "time": "16:05",
                "payee": "PixelPrint Studio",
                "category": "Vendor Payment",
                "amount": 5400.00,
                "channel": "UPI",
            },
            {
                "date": "2026-11-22",
                "time": "11:50",
                "payee": "WorkHub Coworking",
                "category": "Workspace Rent",
                "amount": 12500.00,
                "channel": "NEFT",
            },
            {
                "date": "2026-11-24",
                "time": "14:10",
                "payee": "Ananya Desai (Spouse)",
                "category": "Family Transfer",
                "amount": 8000.00,
                "channel": "UPI",
            },
        ],
    },
}


def get_customer_names() -> List[str]:
    """Return the list of available fictional customer names."""
    return list(CUSTOMERS.keys())


def get_customer_history(customer_name: str) -> pd.DataFrame:
    """Retrieve the selected customer's synthetic transaction history as a DataFrame."""
    if customer_name not in CUSTOMERS:
        raise ValueError(f"Unknown synthetic customer: {customer_name}")

    records = CUSTOMERS[customer_name]["transactions"]
    df = pd.DataFrame(records)
    return df


def _classify_timing_window(hours: List[int]) -> str:
    """Summarize usual transaction hours into a readable time window."""
    if not hours:
        return "No history"

    earliest = min(hours)
    latest = max(hours)

    if earliest >= 6 and latest <= 17:
        period = "Morning to Afternoon"
    elif earliest >= 9 and latest <= 21:
        period = "Daytime & Evening"
    else:
        period = "Mixed Hours"

    return f"{period} ({earliest:02d}:00 – {latest:02d}:59)"


def calculate_behaviour_profile(customer_name: str) -> Dict[str, Any]:
    """Calculate key behavioural baseline metrics for the selected customer.

    Returns:
        Dictionary containing average transaction amount, familiar payees,
        usual transaction timing, number of previous transactions, and metadata.
    """
    if customer_name not in CUSTOMERS:
        raise ValueError(f"Unknown synthetic customer: {customer_name}")

    customer = CUSTOMERS[customer_name]
    df = get_customer_history(customer_name)

    avg_amount = round(float(df["amount"].mean()), 2) if not df.empty else 0.0
    familiar_payees = sorted(df["payee"].unique().tolist()) if not df.empty else []
    hours = [int(t.split(":")[0]) for t in df["time"].tolist()] if not df.empty else []
    usual_timing = _classify_timing_window(hours)
    tx_count = int(len(df))

    return {
        "customer_name": customer_name,
        "customer_id": customer["customer_id"],
        "segment": customer["segment"],
        "normal_behaviour": customer["normal_behaviour"],
        "average_amount": avg_amount,
        "familiar_payees": familiar_payees,
        "usual_timing": usual_timing,
        "transaction_count": tx_count,
    }
