"""
Invoice & Payment Reminder Agent
---------------------------------
Flags invoices past their due date and drafts a payment reminder email
for each one using an LLM.

Input : sample_data/invoices.csv
        columns -> invoice_id, client_name, amount, due_date, status, contact_email
        (status is "paid" or "pending")
Output: output/payment_reminders.txt

Run from the repo root:
    python -m agents.invoice_reminder_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "invoices.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "payment_reminders.txt")

llm = get_llm()


def load_overdue_invoices(path: str) -> pd.DataFrame:
    """Return pending invoices that are past the configured overdue threshold."""
    invoices = pd.read_csv(path, parse_dates=["due_date"])
    today = pd.Timestamp(datetime.date.today())

    is_pending = invoices["status"].str.lower() == "pending"
    invoices["days_overdue"] = (today - invoices["due_date"]).dt.days

    return invoices[is_pending & (invoices["days_overdue"] >= config.INVOICE_OVERDUE_DAYS)]


def draft_reminder_email(row: pd.Series) -> str:
    """Ask the LLM to write a short payment reminder email for one invoice."""
    prompt = f"""You are an accounts receivable coordinator at {config.BUSINESS_NAME}.

Write a short, professional payment reminder email.

Client: {row['client_name']}
Invoice: {row['invoice_id']}
Amount due: {config.CURRENCY_SYMBOL}{row['amount']:,.0f}
Days overdue: {row['days_overdue']}

Requirements:
- Under 90 words
- Polite but clear about the amount and how overdue it is
- Ask for payment or an update by a specific short deadline
- End with "Regards," and leave the sender name blank
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"INVOICE & PAYMENT REMINDER AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find invoices overdue past the configured threshold
    overdue = load_overdue_invoices(INPUT_FILE)

    if overdue.empty:
        print("No overdue invoices. Nothing to do.")
        return

    # Step 2: draft one reminder email per overdue invoice
    drafts = []
    for _, row in overdue.iterrows():
        print(f"Drafting reminder for invoice: {row['invoice_id']} ({row['client_name']})")
        email_text = draft_reminder_email(row)
        drafts.append(
            f"To: {row.get('contact_email', 'client@example.com')}\n"
            f"Subject: Payment Reminder — Invoice {row['invoice_id']}\n\n"
            f"{email_text}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(overdue)} payment reminder(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
