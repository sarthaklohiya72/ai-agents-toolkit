# AI Agents Toolkit

Reusable, production-ready AI agents that solve the operational problems every growing business hits: stock running low without warning, clients going quiet, invoices going unpaid, leads going cold.

Built to be handed to a client, configured for their business in minutes, and run immediately — not rebuilt from scratch per client.

## Why this exists

Most "AI agent" demos are one-off scripts wired to a single company's data. This toolkit is built the other way around: every agent reads its business name, currency, and risk thresholds from one `.env` file, so the same codebase deploys to any client — a textile exporter, a metal fabricator, a retail chain, a service business — by changing configuration, not code.

## Agents included

| # | Agent | Solves |
|---|-------|--------|
| 1 | Inventory Reorder Agent | Stock drops below reorder level with no one noticing until it's a problem |
| 2 | Customer Retention Agent | Clients go quiet and churn without a proactive nudge |
| 3 | Invoice & Payment Reminder Agent | Invoices go unpaid past due date, hurting cash flow |
| 4 | Lead Response Agent | New leads sit unanswered and go cold |
| 5 | Appointment Reminder Agent | No-shows from clients who forgot their appointment |
| 6 | Vendor / Payout Agent | Vendors and contractors chase payment status manually |
| 7 | Weekly Executive Report Agent | Owners spend hours each week compiling a status report by hand |
| 8 | Daily Ops Digest Agent | Ties agents 1–7 into one morning summary of what needs attention |

Every agent follows the same pattern: **read the data → flag the risk → draft the message or report with an LLM.** Drafts are saved to a review file — nothing sends automatically, so a human always approves outbound communication before it goes out.

## Architecture

```
ai-agents-toolkit/
├── config.py                  # Central config — business name, currency, thresholds (from .env)
├── llm_client.py               # Shared LLM client factory (swap providers/models in one place)
├── agents/                     # One file per agent, all following the same pattern
│   ├── inventory_reorder_agent.py
│   ├── customer_retention_agent.py
│   ├── invoice_reminder_agent.py
│   ├── lead_response_agent.py
│   ├── appointment_reminder_agent.py
│   ├── vendor_payment_agent.py
│   ├── weekly_report_agent.py
│   └── daily_digest_agent.py
├── sample_data/                 # Fictional demo data so every agent runs out of the box
└── output/                      # Where drafts and reports are saved (gitignored)
```

## Quick start

```bash
git clone https://github.com/sarthaklohiya72/ai-agents-toolkit
cd ai-agents-toolkit
pip install -r requirements.txt
cp .env.example .env
# edit .env: add your GROQ_API_KEY and the client's business name/currency
```

Run any agent as a module from the repo root:

```bash
python -m agents.inventory_reorder_agent
python -m agents.daily_digest_agent
```

## Configuring for a new client

Everything client-specific lives in `.env` — no code changes needed to onboard a new business:

```env
GROQ_API_KEY=your_key_here
BUSINESS_NAME=Client Business Name
CURRENCY_SYMBOL=₹
DAYS_SINCE_CONTACT_THRESHOLD=30
INVOICE_OVERDUE_DAYS=15
APPOINTMENT_REMINDER_HOURS=24
DATA_DIR=sample_data
OUTPUT_DIR=output
```

Point `DATA_DIR` at the client's real CSVs (or a database export) once they're wired to production data, using the column schema documented in each agent's file header.

## Tech stack

- **Language:** Python 3.11+
- **LLM:** Groq (`llama-3.3-70b-versatile`) via LangChain — fast, low-cost inference
- **Data:** pandas
- **Config:** python-dotenv

## Roadmap

- [ ] Swap CSV inputs for a live database connector (MySQL/Postgres)
- [ ] Add a Streamlit dashboard to review and approve drafts before sending
- [ ] Wire approved drafts to email/WhatsApp send via Make.com or a direct API

## License

MIT — free to use, modify, and deploy for client work.

---

Built by Sarthak Lohiya — AI automation for SME manufacturers and service businesses in Rajasthan & Delhi NCR.
[GitHub](https://github.com/sarthaklohiya72) · [LinkedIn](https://linkedin.com/in/sarthak-lohiya-6a8675275)
