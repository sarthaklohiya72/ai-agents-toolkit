"""
Inventory Reorder Agent
------------------------
Flags products below their reorder level and drafts a supplier reorder
email for each one using an LLM.

Input : sample_data/inventory.csv
        columns -> product_name, current_stock, reorder_level, supplier_name, supplier_email
Output: output/reorder_emails.txt

Run from the repo root:
    python -m agents.inventory_reorder_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "inventory.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "reorder_emails.txt")

llm = get_llm()


def load_low_stock(path: str) -> pd.DataFrame:
    """Return products whose current stock has fallen below their reorder level."""
    inventory = pd.read_csv(path)
    return inventory[inventory["current_stock"] < inventory["reorder_level"]]


def draft_reorder_email(row: pd.Series) -> str:
    """Ask the LLM to write a short reorder email for one product."""
    prompt = f"""You are a purchasing manager at {config.BUSINESS_NAME}.

Write a short, professional reorder email to a supplier.

Product: {row['product_name']}
Current stock: {row['current_stock']} units
Reorder level: {row['reorder_level']} units
Supplier: {row.get('supplier_name', 'Supplier')}

Requirements:
- Under 100 words
- Polite but urgent tone
- Ask for a quote and earliest delivery date
- End with "Regards," and leave the sender name blank
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"INVENTORY REORDER AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find products below reorder level
    low_stock = load_low_stock(INPUT_FILE)

    if low_stock.empty:
        print("All products are above their reorder level. Nothing to do.")
        return

    # Step 2: draft one reorder email per low-stock product
    drafts = []
    for _, row in low_stock.iterrows():
        print(f"Drafting reorder email for: {row['product_name']}")
        email_text = draft_reorder_email(row)
        drafts.append(
            f"To: {row.get('supplier_email', 'supplier@example.com')}\n"
            f"Subject: Reorder Request — {row['product_name']}\n\n"
            f"{email_text}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(low_stock)} reorder email(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
