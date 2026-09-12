"""
Vendor / Payout Agent
-----------------------
Flags vendors or contractors with an outstanding pending payment and
drafts a short payment status message for each one using an LLM.

Input : sample_data/vendors.csv
        columns -> vendor_name, work_type, pending_payment, last_payment_date, contact_email
Output: output/vendor_payment_notices.txt

Run from the repo root:
    python -m agents.vendor_payment_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "vendors.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "vendor_payment_notices.txt")

llm = get_llm()


def load_pending_payments(path: str) -> pd.DataFrame:
    """Return vendors who are owed a pending payment."""
    vendors = pd.read_csv(path)
    return vendors[vendors["pending_payment"] > 0]


def draft_payment_message(row: pd.Series) -> str:
    """Ask the LLM to write a short payment status message for one vendor."""
    prompt = f"""You are a payments coordinator at {config.BUSINESS_NAME}.

Write a short, respectful message to a vendor about their pending payment.

Vendor: {row['vendor_name']}
Work type: {row['work_type']}
Pending amount: {config.CURRENCY_SYMBOL}{row['pending_payment']:,.0f}
Last payment date: {row.get('last_payment_date', 'unknown')}

Requirements:
- Under 70 words
- Respectful and reassuring tone (this is money owed to them, not from them)
- Confirm the amount and give an expected payment timeline
- End with "Regards," and leave the sender name blank
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"VENDOR / PAYOUT AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find vendors who are owed money
    pending = load_pending_payments(INPUT_FILE)

    if pending.empty:
        print("No pending vendor payments. Everyone is paid up.")
        return

    # Step 2: draft one message per vendor with a pending payment
    drafts = []
    for _, row in pending.iterrows():
        print(f"Drafting payment notice for: {row['vendor_name']}")
        message = draft_payment_message(row)
        drafts.append(
            f"Vendor: {row['vendor_name']} ({row['work_type']})\n"
            f"Pending: {config.CURRENCY_SYMBOL}{row['pending_payment']:,.0f} | Contact: {row.get('contact_email', 'n/a')}\n\n"
            f"{message}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(pending)} payment notice(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
