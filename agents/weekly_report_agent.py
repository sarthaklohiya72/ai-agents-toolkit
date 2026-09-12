"""
Weekly Executive Report Agent
-------------------------------
Aggregates invoice and client data into a short weekly executive
report using an LLM — the kind of summary an owner would otherwise
spend an hour compiling by hand every week.

Input : sample_data/invoices.csv, sample_data/clients.csv
Output: output/weekly_report.txt

Run from the repo root:
    python -m agents.weekly_report_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pandas as pd
import config
from llm_client import get_llm

INVOICES_FILE = os.path.join(config.DATA_DIR, "invoices.csv")
CLIENTS_FILE = os.path.join(config.DATA_DIR, "clients.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "weekly_report.txt")

llm = get_llm()


def build_summary_data() -> str:
    """Pull the raw numbers the LLM needs to write this week's report."""
    invoices = pd.read_csv(INVOICES_FILE, parse_dates=["due_date"])
    clients = pd.read_csv(CLIENTS_FILE, parse_dates=["last_contact_date"])

    paid = invoices[invoices["status"].str.lower() == "paid"]
    pending = invoices[invoices["status"].str.lower() == "pending"]

    total_collected = paid["amount"].sum()
    total_pending = pending["amount"].sum()
    top_client = (
        invoices.groupby("client_name")["amount"].sum().idxmax()
        if not invoices.empty else "N/A"
    )

    today = pd.Timestamp(datetime.date.today())
    clients["days_since_contact"] = (today - clients["last_contact_date"]).dt.days
    overdue_clients = clients[clients["days_since_contact"] >= config.DAYS_SINCE_CONTACT_THRESHOLD]

    return f"""
BUSINESS: {config.BUSINESS_NAME}
WEEK OF: {today.strftime('%d %B %Y')}

Revenue collected this period: {config.CURRENCY_SYMBOL}{total_collected:,.0f}
Revenue pending: {config.CURRENCY_SYMBOL}{total_pending:,.0f}
Top client by invoice value: {top_client}
Pending invoice count: {len(pending)}
Clients overdue for contact: {len(overdue_clients)}
"""


def draft_report(summary: str) -> str:
    """Ask the LLM to turn the raw weekly numbers into an executive report."""
    prompt = f"""You are an executive assistant preparing a weekly report for the owner of
{config.BUSINESS_NAME}.

Here is this week's raw data:
{summary}

Write a short executive report:
- Under 150 words
- One line on overall financial health
- Top priority action for the coming week
- Close with a one-line outlook
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"WEEKLY EXECUTIVE REPORT AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: compile this week's raw numbers
    summary = build_summary_data()
    print("Compiling weekly numbers...")

    # Step 2: ask the LLM to write the executive report
    report = draft_report(summary)

    # Step 3: save the report
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)

    print(f"\n{report}")
    print(f"\nReport saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
