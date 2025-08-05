# Service Station Operations MVP Plan

**Goal:** Capture petty cash expenses, fuel logs (with odometer), tasks, and issues via Telegram → GPT → Airtable. Daily summary sent to your Telegram. Exportable report at end.

**Timebox:** Minimum viable system in 3 days.

## 1. High-Level Components

- **Input channel:** Telegram bot (your personal account only for now)
- **Processing/AI:** GPT to classify & extract structured data from free-text messages
- **Storage:** Airtable base with four core tables
- **Reporting:** Daily summary message via Telegram; end-of-run Excel/PDF export
- **Hosting:** Render (backend API and scheduler)

## 2. Airtable Schema (Base Setup)

### Table: Petty Cash

| Field Name | Type | Description |
|------------|------|-------------|
| Date | Date | Transaction date |
| Amount | Currency | Amount spent |
| Description | Long text | What it was for |
| Person | Single line | Who incurred it (initially you) |
| Receipt Photo | Attachment | Optional photo of receipt |
| Theoretical Balance | Formula | Previous day balance minus today's total |
| Actual Balance | Currency | Manual input of actual float counted |
| Reconciliation Diff | Formula | Actual − Theoretical |

**Note:** Seed starting petty cash balance in a separate config record; theoretical balance formula references prior day's theoretical minus sum of that day's outflows.

### Table: Fuel Log

| Field Name | Type | Description |
|------------|------|-------------|
| Date | Date | Fueling date |
| Vehicle | Single select | e.g., "Toyota Hilux" |
| Driver | Single line | Driver name |
| Liters | Number | Quantity dispensed |
| Odometer Start | Number | Before trip (optional for efficiency) |
| Odometer End | Number | After trip |
| KMs Travelled | Formula | End − Start |
| Purpose | Long text | Reason/destination |
| Logged By | Single line | You (for future multi-user) |

### Table: Tasks

| Field Name | Type | Description |
|------------|------|-------------|
| Task | Single line | Short title |
| Details | Long text | Optional expanded description |
| Status | Single select | To Do / In Progress / Done |
| Deadline | Date | When it should be done |
| Assigned To | Single line | (Initially you) |
| Created At | Created time | Auto |
| Notes | Long text | Optional |

### Table: Issues

| Field Name | Type | Description |
|------------|------|-------------|
| Date | Date | Reported date |
| Category | Single select | e.g., Equipment, Supply, Complaint |
| Description | Long text | What happened |
| Severity | Single select | Low / Medium / High |
| Reported By | Single line | You for now |
| Status | Single select | Open / Resolved |
| Resolution Notes | Long text | Optional notes when resolved |

## 3. Telegram → GPT Parsing Design

### Input Style
You just type plain language:

**Examples:**
- "Paid 15,000 MWK for filter replacement from petty cash."
- "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420."
- "Task: Clean backup generator, deadline tomorrow."
- "Issue: Low pressure on pump 2, severity medium."

### GPT Prompt Template

**System instruction:**
You are a structured logger. Given the user message, classify it into one of: expense, fuel, task, issue. Extract relevant fields depending on type. Output JSON with a type field and the appropriate keys:

- **expense:** date (default today), amount, description, person (default "me"), receipt_url (if provided)
- **fuel:** date, vehicle, driver, liters, odometer_start, odometer_end, purpose
- **task:** task_title, details, status (default "To Do"), deadline (if mentioned)
- **issue:** category, description, severity (default "Low" if unspecified), status (default "Open")

**Example expected output:**
```json
{
  "type": "expense",
  "date": "2025-08-04",
  "amount": 15000,
  "description": "Filter replacement",
  "person": "Me"
}
```

**Implementation:**
- Send user message to GPT (use gpt-4o-mini or similar for speed)
- Parse JSON response; validate required fields
- Map and upsert into the correct Airtable table via Airtable API

## 4. Backend Service (Cursor Project)

**Tech stack:** Python (FastAPI)

**Endpoints:**
- `/telegram-webhook` — receives updates from Telegram
- Internal handler to call OpenAI, parse the message, and write to Airtable
- `/daily-summary` — triggered by scheduler to gather and send summary

### Key Modules to Build (MVP order)

#### Day 1:
1. [ ] Telegram bot setup (polling or webhook)
2. [ ] Airtable connection utility
3. [ ] GPT inference module with the prompt and basic parsing
4. [ ] Handler to take a Telegram message, classify it, and write to Airtable with minimal confirmation reply
   - Confirm back like: "Logged expense: 15,000 MWK for filter replacement. Theoretical petty cash left: XX."

#### Day 2:
5. [ ] Implement the four table schemas in Airtable and test inserts
6. [ ] Fuel log with odometer handling (calculate kms)
7. [ ] Tasks and issues logging
8. [ ] Build the daily summary generator:
   - Query today's petty cash outflows + current theoretical vs actual
   - Fuel dispensed summary (vehicle, total liters, kms)
   - Pending tasks (count and titles)
   - New issues (count, high severity)
9. [ ] Telegram summary sender at a fixed time (cron-like scheduler on Render)

#### Day 3:
10. [ ] Add manual actual petty cash reconciliation entry with diff calculation
11. [ ] Build final export:
    - Pull full 2-week data from each Airtable table
    - Generate Excel (using openpyxl/pandas) and optional PDF summary
    - Provide a command like `/export` to trigger attachment link via Telegram
12. [ ] Buffer/testing/fixes and documentation of usage

## 5. Daily Summary Format (Telegram)

**Example:**
```
Daily Summary – Aug 4, 2025
• Petty Cash: Spent 23,500 MWK today. Theoretical balance: 76,500 MWK. Actual float (if entered): 75,000 MWK. Diff: −1,500 MWK.
• Fuel: 65L dispensed: Hilux (40L, 120 km), Toyota Prado (25L, 80 km).
• Tasks: 3 pending (Clean generator, Refill oil, Inventory count).
• Issues: 1 new (Pump 2 pressure low, severity: Medium).
```

## 6. Export & Backup

- Endpoint or command (`/export`) triggers:
  - Fetch all records in CSV/Excel: one sheet per table
  - Summary page (automatically generated) with key totals
  - Bundle and store in `/mnt/data` or equivalent, then send download link via Telegram
  - Optionally, use a simple PDF generator for the summary

## 7. Deployment on Render

- Create a service for your API (Python app)
- Environment variables:
  - `TELEGRAM_TOKEN`, `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `OPENAI_API_KEY`, summary schedule time
- Use Render cron job or internal scheduler to hit `/daily-summary` at, e.g., 17:00 local time (Africa/Blantyre UTC+2)

## 8. Minimum Viable Commands

- Free-text entries (expense, fuel, task, issue) — parsed automatically
- `/status` — immediate snapshot of current petty cash balance, pending tasks, and open issues
- `/export` — get full Excel/PDF export
- `/help` — instructions on phrasing

## 9. MVP Success Criteria (by end of Day 3)

- [ ] Telegram bot accepts plain sentences and logs to correct Airtable tables
- [ ] Petty cash theoretical vs actual reconciliation works
- [ ] Fuel entries with odometer and km calculation appear correctly
- [ ] Tasks and issues can be created and updated manually
- [ ] Daily summary is sent automatically
- [ ] `/export` produces a downloadable Excel with all data

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| GPT misclassification of message | Keep reply confirmations; allow manual correction via follow-up |
| Airtable rate limits / schema mismatch | Start with minimal fields; validate before writes; add retries/backoff |
| Timezone mismatch for scheduling | Use absolute UTC scheduling on Render after converting Africa/Blantyre local time |
| Losing data if bot crashes | Logging of incoming messages; consider a simple queue / retry mechanism |
| Export file size or failure | Keep dataset small (2 weeks), test generation locally first |

## 11. Immediate Next Actions (Today, Day 1)

1. [ ] Create Airtable base with the 4 tables and set up initial fields
2. [ ] Provision Telegram bot and get token
3. [ ] Scaffold Cursor project: endpoint, env config, connect to Telegram and Airtable
4. [ ] Implement GPT parsing for at least one type (start with petty cash expense)
5. [ ] Test a few example messages end-to-end (Telegram → GPT → Airtable → confirmation)

## 12. Error Handling & Edge Cases

### Fallback Clarifier
If required fields are missing or ambiguous, bot replies: "I didn't fully understand — did you mean an expense for 15,000 MWK for pump repair from petty cash? Reply Y to confirm or rephrase."

### Edit Command
Define an "edit" syntax: `/edit [record_id] field=value` for quick manual correction in Telegram.

### Petty Cash Seed Setup
Have a config table/record with Starting Balance and a formula field in Petty Cash that references previous day's theoretical using a rollup or scripting extension.

## 13. Self-Critique

### Strengths in Plan
- Clear MVP scope and prioritized order for 3-day execution
- Structured Airtable schema aligning with clarified needs
- GPT prompt templates and examples reduce ambiguity
- Daily summary and export included for end-of-run reporting
- Risks identified with reasonable mitigations

### Potential Gaps / Improvements
1. Reconciliation logic detail for petty cash theoretical balance needs explicit formula setup
2. Error correction interface is minimal; no built-in "edit" command spec
3. Authentication/spoof protection: currently assumes only you; future handoff would need user identification
4. Edge cases for ambiguous messages aren't explicitly handled
5. Export formatting: exact template for summary sheet could be pre-defined

### Adjustments Applied
- Added fallback clarifier step for ambiguous messages
- Specified petty cash seed setup with config table/record
- Defined edit syntax for quick manual correction
- Included GPT system prompt drafting in immediate tasks

---

**Created:** [Date]
**Last Updated:** [Date]
**Status:** Unimplemented 