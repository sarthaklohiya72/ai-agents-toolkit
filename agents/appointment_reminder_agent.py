"""
Appointment Reminder Agent
----------------------------
Finds upcoming appointments within the reminder window and drafts a
short reminder message for each one using an LLM.

Input : sample_data/appointments.csv
        columns -> client_name, appointment_datetime, service, contact_email
Output: output/appointment_reminders.txt

Run from the repo root:
    python -m agents.appointment_reminder_agent
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import pandas as pd
import config
from llm_client import get_llm

INPUT_FILE = os.path.join(config.DATA_DIR, "appointments.csv")
OUTPUT_FILE = os.path.join(config.OUTPUT_DIR, "appointment_reminders.txt")

llm = get_llm()


def load_upcoming_appointments(path: str) -> pd.DataFrame:
    """Return appointments happening within the configured reminder window."""
    appointments = pd.read_csv(path, parse_dates=["appointment_datetime"])
    now = pd.Timestamp(datetime.datetime.now())
    window_end = now + pd.Timedelta(hours=config.APPOINTMENT_REMINDER_HOURS)

    return appointments[
        (appointments["appointment_datetime"] >= now)
        & (appointments["appointment_datetime"] <= window_end)
    ]


def draft_reminder_message(row: pd.Series) -> str:
    """Ask the LLM to write a short reminder message for one appointment."""
    prompt = f"""You are a front-desk coordinator at {config.BUSINESS_NAME}.

Write a short, friendly appointment reminder message.

Client: {row['client_name']}
Service: {row['service']}
Appointment time: {row['appointment_datetime']}

Requirements:
- Under 50 words
- Friendly and clear
- Ask them to reply if they need to reschedule
"""
    return llm.invoke(prompt).content


def run():
    print("\n" + "=" * 60)
    print(f"APPOINTMENT REMINDER AGENT — {config.BUSINESS_NAME}")
    print("=" * 60 + "\n")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # Step 1: find appointments coming up within the reminder window
    upcoming = load_upcoming_appointments(INPUT_FILE)

    if upcoming.empty:
        print("No appointments in the reminder window.")
        return

    # Step 2: draft one reminder per upcoming appointment
    drafts = []
    for _, row in upcoming.iterrows():
        print(f"Drafting reminder for: {row['client_name']} at {row['appointment_datetime']}")
        message = draft_reminder_message(row)
        drafts.append(
            f"To: {row.get('contact_email', 'client@example.com')}\n"
            f"Appointment: {row['client_name']} — {row['service']} at {row['appointment_datetime']}\n\n"
            f"{message}\n" + "-" * 60
        )

    # Step 3: save all drafts for review before sending
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n\n".join(drafts))

    print(f"\n{len(upcoming)} appointment reminder(s) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
