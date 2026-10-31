# 📊 Indian Index Options OI Alert Bot

An asynchronous Python-based Telegram bot designed to monitor Open Interest (OI), option-chain activity, and market movements across Indian indices.

The bot continuously monitors configurable market conditions and delivers real-time alerts to Telegram when user-defined thresholds and conditions are satisfied.

**Alert-only system:** This application does not execute, place, modify, or cancel any trading orders.

---

## 🚀 Project Overview

The Indian Index Options OI Alert Bot monitors options market data for selected Indian indices and generates configurable Telegram alerts.

The initial release focuses on:

- NIFTY 50
- BANKNIFTY

The architecture supports adding additional indices in future releases through a modular index registry.

### Key Objectives

- Monitor CE and PE Open Interest across selected strikes.
- Calculate rolling OI changes over 5, 15, and 30-minute windows.
- Monitor Put-Call Ratio (PCR).
- Track option premiums, volume, implied volatility, and index spot prices.
- Generate alerts based on configurable market conditions.
- Prevent duplicate notifications using cooldown mechanisms.
- Manage alert configurations directly through Telegram.
- Maintain configuration and historical state across application restarts.
- Run continuously on an Ubuntu VPS.

---

## ✨ Features

### 1. Market Data Monitoring

The application is designed to monitor:

| Metric | Description |
|---|---|
| Open Interest | CE and PE OI by strike |
| OI Change | Change compared with previous close |
| Rolling OI Change | 5, 15, and 30-minute changes |
| PCR | Overall and expiry-wise Put-Call Ratio |
| Option Premium | Last Traded Price (LTP) |
| Volume | Trading volume by strike |
| Implied Volatility | IV for individual strikes |
| Index Spot | Live index spot price |
| Expiry | Weekly and monthly expiry selection |

### 2. Configurable Strike Monitoring

- Automatically identify the At-The-Money (ATM) strike.
- Monitor configurable strikes around ATM.
- Default configuration can be set to ±15 strikes.
- Support percentage-based strike ranges.
- Avoid unnecessary full option-chain processing.

### 3. Alert Engine

The bot supports the following alert categories:

| Alert Type | Example |
|---|---|
| OI Level | BANKNIFTY 52000 CE OI > 2500000 |
| OI Change | OI increased by more than 20% in 15 minutes |
| PCR | PCR < 0.8 or PCR > 1.5 |
| Premium / LTP | NIFTY 25500 PE LTP > 150 |
| Index Spot | BANKNIFTY crosses 52000 |
| Highest OI Strike | Alert when the highest OI strike changes |
| Max Pain | Optional daily EOD Max Pain summary |

Each alert can be configured using:

- Index
- Expiry
- Strike
- Option type (CE / PE)
- Condition/operator
- Threshold value
- Cooldown duration

### 4. Telegram Integration

Telegram is the primary interface for interacting with the application.

#### Supported Commands

| Command | Description |
|---|---|
| `/start` | Start interacting with the bot |
| `/add` | Create a new alert |
| `/remove <id>` | Remove an existing alert |
| `/list` | Display configured alerts |
| `/pause <id>` | Pause a specific alert |
| `/resume <id>` | Resume a paused alert |
| `/pause all` | Pause all alerts |
| `/status` | Display bot health and data-feed status |
| `/set cooldown <minutes>` | Configure alert cooldown |
| `/set strikes <count>` | Configure ATM strike range |
| `/set interval <minutes>` | Configure data-refresh interval |
| `/help` | Display available commands |

Example:

```text
/add BANKNIFTY 52000 CE OI > 2500000
```

Example Telegram notification:

```text
🔔 OPEN INTEREST ALERT

Index: BANKNIFTY
Strike: 52000 CE
Expiry: 23 Oct

Condition: OI > 25,00,000
Current OI: 26,40,000

Time: 11:42 AM IST
```

*Illustrative notification with sample values.*

### 5. Anti-Spam Mechanism

The alert engine includes:

- Per-alert cooldown configuration.
- Default cooldown of 20 minutes.
- Duplicate alert prevention.
- Individual alert pause and resume.
- Global pause functionality.
- Alert state persistence.

### 6. Rolling OI Calculation

Broker APIs may provide current OI snapshots rather than the complete historical rolling-window data required by the application.

The bot maintains local timestamped snapshots to calculate rolling changes.

Formula:

```text
OI Change Percentage =

((Current OI - Previous OI) / Previous OI) * 100
```

Example:

```text
OI 15 minutes ago: 10,00,000
Current OI:        12,00,000

OI Change:         +20%
```

The rolling calculation supports:

- 5-minute window
- 15-minute window
- 30-minute window

Local history is maintained using a persistent storage mechanism.

---

## 🏗️ System Architecture

```text
                  TELEGRAM USER
                        |
                        v
                  TELEGRAM BOT
                        |
                        v
               TELEGRAM COMMAND HANDLER
                        |
                        v
                 PYTHON APPLICATION
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      MARKET DATA   ALERT ENGINE   SCHEDULER
       SERVICE          |             |
          |             |             |
          v             v             v
      BROKER API    RULE EVALUATION  MARKET HOURS
          |             |
          v             v
     OPTION CHAIN   COOLDOWN SERVICE
          |             |
          +------+------+
                 |
                 v
             PERSISTENCE
                 |
          +------+------+
          |             |
          v             v
       SQLITE         YAML
          |             |
          +------+------+
                 |
                 v
           TELEGRAM ALERT
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Architecture | Asynchronous |
| Async Runtime | asyncio |
| HTTP Client | aiohttp |
| Telegram Integration | Telegram Bot API |
| Configuration | YAML |
| Environment Variables | python-dotenv |
| Local Persistence | SQLite |
| Data Processing | Python |
| Logging | Python Logging |
| Deployment | Ubuntu VPS |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |

---

## 📡 Market Data Provider

The application is designed to integrate with an authorized Indian broker market-data API.

Potential providers:

1. DhanHQ
2. Angel One SmartAPI

The final provider will be selected after validating:

- Option-chain API availability.
- CE/PE OI and previous-close OI data.
- Option LTP, volume, and IV availability.
- Authentication and token-refresh requirements.
- API rate limits.
- Market-data subscription costs.
- Data reliability and permitted usage.

**Important:** NSE website scraping is strictly avoided.

The broker integration must comply with the provider's API terms and market-data licensing requirements.

---

## ⏰ Market Operating Hours

The application is designed to operate according to Indian market hours.

| Setting | Configuration |
|---|---|
| Timezone | Asia/Kolkata |
| Market Start | 09:15 AM IST |
| Market End | 03:30 PM IST |
| Operating Days | Monday–Friday |
| Data Refresh | Configurable 1–5 minutes |
| Default Cooldown | 20 minutes |
| EOD Summary | Optional, 03:35 PM IST |

The scheduler must skip NSE trading holidays and account for applicable special trading sessions or half-days.

---

## 📁 Project Structure

```text
indian-market-oi-alert-bot/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   └── config_loader.py
│   │
│   ├── telegram/
│   │   ├── bot.py
│   │   ├── commands.py
│   │   └── notifications.py
│   │
│   ├── market/
│   │   ├── market_data_client.py
│   │   ├── option_chain.py
│   │   ├── expiry_manager.py
│   │   └── index_registry.py
│   │
│   ├── oi/
│   │   ├── oi_calculator.py
│   │   ├── rolling_window.py
│   │   └── pcr_calculator.py
│   │
│   ├── alerts/
│   │   ├── alert_engine.py
│   │   ├── alert_rules.py
│   │   └── cooldown_manager.py
│   │
│   ├── scheduler/
│   │   ├── market_scheduler.py
│   │   └── holiday_manager.py
│   │
│   ├── storage/
│   │   ├── database.py
│   │   └── config_repository.py
│   │
│   └── monitoring/
│       ├── health_monitor.py
│       └── logger.py
│
├── tests/
│   ├── test_oi_calculator.py
│   ├── test_rolling_window.py
│   ├── test_alert_engine.py
│   └── test_cooldown.py
│
├── data/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── config.yaml.example
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

*The structure represents the proposed architecture; individual modules can be added as development progresses.*

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.12 or later.
- Telegram account.
- Telegram bot token.
- Authorized broker API credentials.
- Ubuntu VPS for production deployment.

### 1. Clone Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>

cd indian-market-oi-alert-bot
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file using `.env.example`.

Example:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

BROKER_NAME=dhan

BROKER_CLIENT_ID=your_client_id
BROKER_ACCESS_TOKEN=your_access_token
BROKER_API_KEY=your_api_key
BROKER_TOTP_SECRET=your_totp_secret

TIMEZONE=Asia/Kolkata
LOG_LEVEL=INFO
```

The actual required broker credentials depend on the selected provider and authentication flow.

### 5. Configure Application Settings

Create `config.yaml` using `config.yaml.example`.

Example:

```yaml
application:
  name: indian-market-oi-alert-bot
  timezone: Asia/Kolkata

market:
  indices:
    - NIFTY
    - BANKNIFTY

  start_time: "09:15"
  end_time: "15:30"

  polling_interval: 5

  strike_range:
    mode: count
    value: 15

alerts:
  default_cooldown: 20

  rolling_windows:
    - 5
    - 15
    - 30

telegram:
  enabled: true
  group_support: false

storage:
  type: sqlite
  database: data/oi_alerts.db

logging:
  level: INFO
  rotation: true
```

### 6. Run the Application

```bash
python -m app.main
```

---

## 🔐 Security

Security considerations:

- Store all API credentials in environment variables.
- Never hard-code tokens or secrets.
- Exclude `.env` from Git.
- Restrict Telegram commands to authorized user IDs.
- Protect broker authentication credentials.
- Avoid logging tokens, TOTP secrets or sensitive API responses.
- Use HTTPS for supported webhook deployments.
- Secure VPS access and file permissions.

---

## 📈 Reliability and Monitoring

The production application is designed to include:

- Structured application logs.
- Rotating log files.
- API timeout handling.
- Exponential backoff.
- Broker rate-limit handling.
- Market-data freshness validation.
- Telegram notification on prolonged data-feed failure.
- Automatic restart after application crash.
- Configuration recovery after server reboot.
- Graceful shutdown and recovery.

---

## 🐳 Deployment

The application is intended to run continuously on an Ubuntu VPS.

Supported deployment approaches:

**Option 1: Docker Compose**

```bash
docker compose up -d --build
```

**Option 2: systemd**

```bash
sudo systemctl enable oi-alert-bot

sudo systemctl start oi-alert-bot
```

Check application status:

```bash
sudo systemctl status oi-alert-bot
```

View logs:

```bash
docker compose logs -f
```

---

## 🧪 Testing and Acceptance Criteria

The application will be tested against the following acceptance criteria:

- Run continuously for two complete trading days without crashing.
- Verify at least three alert conditions.
- Verify Telegram configuration persistence after server reboot.
- Validate cooldown and duplicate-alert prevention.
- Verify rolling OI calculations for all configured windows.
- Test broker API failures and recovery.
- Validate market-hour and NSE holiday handling.
- Verify structured logs and operational health reporting.

---

## 🚫 Out of Scope

The application will not:

- Place trading orders.
- Modify or cancel trading orders.
- Execute automated trading strategies.
- Provide investment recommendations.
- Provide a separate web or mobile user interface.

Telegram is the only user interface.

---

## 🗺️ Development Roadmap

- [ ] Python project initialization.
- [ ] Telegram bot integration.
- [ ] Telegram command handling.
- [ ] Broker API integration.
- [ ] NIFTY 50 option-chain monitoring.
- [ ] BANKNIFTY option-chain monitoring.
- [ ] Rolling OI calculations.
- [ ] PCR calculations.
- [ ] Configurable alert engine.
- [ ] Cooldown and duplicate prevention.
- [ ] YAML configuration persistence.
- [ ] SQLite historical data storage.
- [ ] Market-hour and holiday management.
- [ ] API failure monitoring.
- [ ] Automated testing.
- [ ] Docker deployment.
- [ ] VPS production deployment.
- [ ] Two-trading-day acceptance test.

---

## 📌 Project Status

**Initial development / implementation in progress.**

This repository is intended to contain the complete source code, configuration templates, automated tests, documentation and deployment resources as development progresses.

---

## 📄 License

License to be defined by the project owner.

---

## ⚠️ Disclaimer

This software is intended solely for market-data monitoring and informational alert delivery.

It does not execute trades or provide financial advice.

Market data may be delayed, incomplete or unavailable depending on the selected provider. Users should independently verify information before making financial decisions.

---

**Project:** Indian Index Options OI Alert Bot  
**Version:** 2.0  
**Market:** Indian Derivatives Market  
**Initial Indices:** NIFTY 50 and BANKNIFTY  
**Interface:** Telegram  
**Architecture:** Asynchronous Python