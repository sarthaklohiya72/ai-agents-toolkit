"""
Customer Retention Agent
------------------------
Flags clients who haven't been contacted recently and drafts a
personalized re-engagement message for each one using an LLM.

Input : sample_data/clients.csv
        columns -> client_name, last_contact_date, contact_email
Output: output/retention_messages.txt

Run from the repo root:
    python -m agents.customer_retention_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "clients.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "retention_messages.txt")

llm = get_llm()


def load_at_risk_clients(path: str) -> pd.DataFrame:
    """Return clients not contacted within the configured risk threshold."""
    clients = pd.read_csv(path, parse_dates=["last_contact_date"])
    today = pd.Timestamp(datetime.date.today())
    clients["days_since_contact"] = (today - clients["last_contact_date"]).dt.days
    return clients[clients["days_since_contact"] >= config.DAYS_SINCE_CONTACT_THRESHOLD]


def draft_retention_message(row: pd.Series) -> str:
    """Ask the LLM to write a short check-in message for one client."""
    prompt = f"""You are a relationship manager at {config.BUSINESS_NAME}.

Write a short, warm check-in message to a client we haven't spoken to in a while.

Client: {row['client_name']}
Days since last contact: {row['days_since_contact']}

Requirements:
- Under 80 words
- Friendly, not salesy
- Reference that it's been a while
- Ask if they have any upcoming requirements
- End with "Regards," and leave the sender name blank
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"CUSTOMER RETENTION AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find clients overdue for contact
    at_risk = load_at_risk_clients(INPUT_FILE)

    if at_risk.empty:
        print("All clients have been contacted recently. Nothing to do.")
        return

    # Step 2: draft one message per at-risk client
    drafts = []
    for _, row in at_risk.iterrows():
        print(f"Drafting retention message for: {row['client_name']}")
        message = draft_retention_message(row)
        drafts.append(
            f"To: {row.get('contact_email', 'client@example.com')}\n"
            f"Client: {row['client_name']} ({row['days_since_contact']} days since contact)\n\n"
            f"{message}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(at_risk)} retention message(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
