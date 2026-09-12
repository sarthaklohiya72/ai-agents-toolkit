"""
Shared configuration for every agent in this toolkit.

Each agent reads its settings from environment variables (via .env), so the
same codebase deploys to any client by changing configuration, not code.

Copy .env.example to .env and fill in your values before running any agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Business identity ---
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Your Business")
CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "$")

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Risk thresholds (tune per client) ---
DAYS_SINCE_CONTACT_THRESHOLD = int(os.getenv("DAYS_SINCE_CONTACT_THRESHOLD", "30"))
INVOICE_OVERDUE_DAYS = int(os.getenv("INVOICE_OVERDUE_DAYS", "15"))
APPOINTMENT_REMINDER_HOURS = int(os.getenv("APPOINTMENT_REMINDER_HOURS", "24"))

# --- File paths (override per client if their data lives elsewhere) ---
DATA_DIR = os.getenv("DATA_DIR", "sample_data")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
