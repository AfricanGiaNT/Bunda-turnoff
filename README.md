# Service Station Operations Bot

A Telegram bot for managing service station operations including petty cash expenses, fuel logs, tasks, and issues. Uses GPT for natural language processing and Airtable for data storage.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Airtable API Key and Base ID

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Bunda-turnoff
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp config/example.env .env
   # Edit .env with your actual API keys and configuration
   ```

4. **Set up Airtable base**
   - Create a new Airtable base
   - Create the required tables (Petty Cash, Fuel Log, Tasks, Issues)
   - Use the schema defined in `plans/unimplemented/service-station-ops-mvp.md`

5. **Run the bot**
   ```bash
   uvicorn api.telegram_handler:app --reload
   ```

## 📋 Features

- **Natural Language Processing**: Send plain text messages to log expenses, fuel, tasks, and issues
- **Daily Summaries**: Automatic daily summaries sent via Telegram
- **Export Functionality**: Generate Excel/PDF reports
- **Petty Cash Tracking**: Theoretical vs actual balance reconciliation
- **Fuel Logging**: Track fuel consumption with odometer readings
- **Task Management**: Create and track tasks with deadlines
- **Issue Tracking**: Log and categorize issues by severity

## 🗂️ Project Structure

```
/
├── api/                    # Backend service modules
│   ├── telegram_handler.py # Telegram webhook/polling entrypoints
│   ├── gpt_parser.py       # GPT prompt construction + response interpretation
│   ├── airtable_client.py  # Airtable read/write abstractions
│   ├── summary_generator.py # Daily summary logic
│   └── exporter.py         # Excel/PDF export logic
├── utils/                  # Shared helpers
│   ├── datetime_utils.py   # Timezone conversion utilities
│   ├── retry_utils.py      # Retry/backoff logic
│   └── logging_config.py   # Logging configuration
├── plans/                  # Execution plans and lifecycle
│   ├── unimplemented/      # Plans defined but not yet fully coded
│   ├── implemented/        # Plans confirmed complete
│   └── plan_manager.py     # Script that detects completion and moves plan files
├── tests/                  # Automated and manual test definitions
│   ├── unit/              # Unit tests for individual modules
│   ├── integration/       # End-to-end tests
│   └── test_runner.py     # Entrypoint to run all relevant tests
├── config/                # Environment-agnostic configuration
│   ├── example.env        # Template for environment variables
│   └── airtable_seed.json # Initial data (vehicles, task templates, etc.)
├── scripts/               # Ad-hoc scripts
├── docs/                  # Human-facing documentation
├── deploy/                # Deployment helpers
│   └── render.yaml        # Render service + cron job manifest
└── requirements.txt       # Python dependencies
```

## 🤖 Usage

### Telegram Commands

- **Free-text entries**: Just send natural language messages like:
  - "Paid 15,000 MWK for filter replacement from petty cash"
  - "Gave 40 liters diesel to Hilux, driver John, for Salima trip"
  - "Task: Clean backup generator, deadline tomorrow"
  - "Issue: Low pressure on pump 2, severity medium"

- **Special commands**:
  - `/status` - Get current status snapshot
  - `/export` - Generate Excel/PDF export
  - `/help` - Show usage instructions
  - `/plan-status` - List plan completion status

### Daily Summary Format

```
Daily Summary – Aug 4, 2025
• Petty Cash: Spent 23,500 MWK today. Theoretical balance: 76,500 MWK.
• Fuel: 65L dispensed: Hilux (40L, 120 km), Toyota Prado (25L, 80 km).
• Tasks: 3 pending (Clean generator, Refill oil, Inventory count).
• Issues: 1 new (Pump 2 pressure low, severity: Medium).
```

## 🧪 Testing

Run tests using the test runner:

```bash
# Run all tests
python tests/test_runner.py

# Run only unit tests
python tests/test_runner.py --unit

# Run only integration tests
python tests/test_runner.py --integration

# Run with coverage
python tests/test_runner.py --coverage

# Show test summary
python tests/test_runner.py --summary
```

## 📊 Plan Management

Manage execution plans:

```bash
# Check and promote completed plans
python plans/plan_manager.py --check

# Show plan status
python plans/plan_manager.py --status

# List all plans
python plans/plan_manager.py --list
```

## 🚀 Deployment

### Render Deployment

1. **Connect your repository** to Render
2. **Use the provided** `deploy/render.yaml` configuration
3. **Set environment variables** in Render dashboard
4. **Deploy** - Render will automatically set up both the web service and cron job

### Environment Variables

Required environment variables:
- `TELEGRAM_TOKEN` - Your Telegram bot token
- `OPENAI_API_KEY` - Your OpenAI API key
- `AIRTABLE_API_KEY` - Your Airtable API key
- `AIRTABLE_BASE_ID` - Your Airtable base ID
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID for receiving summaries

Optional:
- `DAILY_SUMMARY_TIME_UTC` - Time for daily summaries (default: 15:00)
- `STARTING_PETTY_CASH` - Initial petty cash balance (default: 100000)
- `LOG_LEVEL` - Logging level (default: INFO)

## 🔧 Development

### Adding New Features

1. **Create a plan** in `plans/unimplemented/`
2. **Implement the feature** following the project structure
3. **Write tests** in the appropriate test directory
4. **Update the plan** with completion checkmarks
5. **Run the plan manager** to promote completed plans

### Code Style

- Follow PEP 8 for Python code
- Use type hints throughout
- Add docstrings to all functions and classes
- Use the logging utilities for all logging

## 📝 License

This project is for personal use. All rights reserved.

## 🤝 Contributing

This is a personal project for managing service station operations. No external contributions are expected.

---

**Status**: MVP in development (see `plans/unimplemented/service-station-ops-mvp.md` for detailed implementation plan) 