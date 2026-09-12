"""
Lead Response Agent
--------------------
Finds new, unanswered leads and drafts a personalized first-response
message for each one using an LLM.

Input : sample_data/leads.csv
        columns -> lead_name, contact_email, inquiry, source, status
        (status is "new" or "contacted")
Output: output/lead_responses.txt

Run from the repo root:
    python -m agents.lead_response_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "leads.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "lead_responses.txt")

llm = get_llm()


def load_new_leads(path: str) -> pd.DataFrame:
    """Return leads that haven't been contacted yet."""
    leads = pd.read_csv(path)
    return leads[leads["status"].str.lower() == "new"]


def draft_lead_response(row: pd.Series) -> str:
    """Ask the LLM to write a short first-response email for one lead."""
    prompt = f"""You are a sales coordinator at {config.BUSINESS_NAME}.

Write a short, friendly first-response email to a new inbound lead.

Lead name: {row['lead_name']}
Source: {row.get('source', 'website')}
Their inquiry: {row['inquiry']}

Requirements:
- Under 90 words
- Thank them for reaching out
- Directly address their specific inquiry
- End with a clear next step (a call, a quote, or a question)
- End with "Regards," and leave the sender name blank
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"LEAD RESPONSE AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find leads that haven't had a first response yet
    new_leads = load_new_leads(INPUT_FILE)

    if new_leads.empty:
        print("No new leads waiting on a response.")
        return

    # Step 2: draft one response per new lead
    drafts = []
    for _, row in new_leads.iterrows():
        print(f"Drafting response for lead: {row['lead_name']}")
        response = draft_lead_response(row)
        drafts.append(
            f"To: {row.get('contact_email', 'lead@example.com')}\n"
            f"Lead: {row['lead_name']} (source: {row.get('source', 'unknown')})\n\n"
            f"{response}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(new_leads)} lead response(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
