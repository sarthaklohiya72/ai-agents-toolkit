"""
Daily Ops Digest Agent
-----------------------
Ties together every risk-check agent in this toolkit into one morning
digest: low stock, overdue clients, overdue invoices, unanswered leads,
upcoming appointments, and pending vendor payments — all in one short
summary instead of six separate output files.

Input : all files in sample_data/
Output: output/daily_digest.txt

Run from the repo root:
    python -m agents.daily_digest_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pandas as pd
import config
from llm_client import get_llm

OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "daily_digest.txt")

llm = get_llm()


def safe_count(fn) -> int:
    """Run a counter function, treating a missing/unreadable CSV as zero risk."""
    try:
        return fn()
    except (FileNotFoundError, KeyError):
        return 0


def count_low_stock() -> int:
    inventory = pd.read_csv(os.path.join(config.DATA_DIR, "inventory.csv"))
    return len(inventory[inventory["current_stock"] < inventory["reorder_level"]])


def count_overdue_clients() -> int:
    clients = pd.read_csv(os.path.join(config.DATA_DIR, "clients.csv"), parse_dates=["last_contact_date"])
    today = pd.Timestamp(datetime.date.today())
    clients["days_since_contact"] = (today - clients["last_contact_date"]).dt.days
    return len(clients[clients["days_since_contact"] >= config.DAYS_SINCE_CONTACT_THRESHOLD])


def count_overdue_invoices() -> int:
    invoices = pd.read_csv(os.path.join(config.DATA_DIR, "invoices.csv"), parse_dates=["due_date"])
    today = pd.Timestamp(datetime.date.today())
    is_pending = invoices["status"].str.lower() == "pending"
    days_overdue = (today - invoices["due_date"]).dt.days
    return len(invoices[is_pending & (days_overdue >= config.INVOICE_OVERDUE_DAYS)])


def count_new_leads() -> int:
    leads = pd.read_csv(os.path.join(config.DATA_DIR, "leads.csv"))
    return len(leads[leads["status"].str.lower() == "new"])


def count_upcoming_appointments() -> int:
    appointments = pd.read_csv(os.path.join(config.DATA_DIR, "appointments.csv"), parse_dates=["appointment_datetime"])
    now = pd.Timestamp(datetime.datetime.now())
    window_end = now + pd.Timedelta(hours=config.APPOINTMENT_REMINDER_HOURS)
    return len(
        appointments[
            (appointments["appointment_datetime"] >= now)
            & (appointments["appointment_datetime"] <= window_end)
        ]
    )


def count_pending_vendor_payments() -> int:
    vendors = pd.read_csv(os.path.join(config.DATA_DIR, "vendors.csv"))
    return len(vendors[vendors["pending_payment"] > 0])


def draft_digest(counts: dict) -> str:
    """Ask the LLM to turn six risk counts into one short executive digest."""
    today = datetime.date.today().strftime("%d %B %Y")
    prompt = f"""You are an operations assistant for {config.BUSINESS_NAME}.

Today is {today}. Here are today's risk counts from six monitoring agents:

- Low stock items needing reorder: {counts['low_stock']}
- Clients overdue for contact: {counts['overdue_clients']}
- Invoices overdue for payment: {counts['overdue_invoices']}
- New leads awaiting a response: {counts['new_leads']}
- Appointments coming up soon: {counts['upcoming_appointments']}
- Vendors with pending payments: {counts['pending_vendor_payments']}

Write a short "Daily Ops Digest" for the owner:
- Under 130 words
- Open with one line on overall status (calm day vs. needs attention)
- List the single top priority to act on today
- Mention that details are in each agent's own output file
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"DAILY OPS DIGEST AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: gather counts from all six risk areas
    counts = {
        "low_stock": safe_count(count_low_stock),
        "overdue_clients": safe_count(count_overdue_clients),
        "overdue_invoices": safe_count(count_overdue_invoices),
        "new_leads": safe_count(count_new_leads),
        "upcoming_appointments": safe_count(count_upcoming_appointments),
        "pending_vendor_payments": safe_count(count_pending_vendor_payments),
    }

    print("Risk counts today:")
    for key, value in counts.items():
        print(f"  {key}: {value}")

    # Step 2: ask the LLM to turn the counts into a short, readable digest
    print("\nDrafting digest...")
    digest = draft_digest(counts)

    # Step 3: save the digest for the owner to read each morning
    with open(OUTPUT_FILE, "w") as f:
        f.write(digest)

    print(f"\n{digest}")
    print(f"\nDigest saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
