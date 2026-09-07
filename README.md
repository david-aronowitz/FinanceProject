הבנתי בדיוק! הבעיה נובעת מכך שבממשק של Gemini, כשאני שולח קוד Markdown בתוך תיבת קוד רגילה, הבלוקים של ה-Code Blocks של הפקודות או המבנה חותכים ומפרקים את התיבה הראשית לחלקים נפרדים.

כדי לפתור את זה באופן מוחלט, הנה **כל הקובץ בתוך תיבת קוד אחת נקייה ללא שום תגיות Markdown פנימיות שיכולות לשבור אותה**.

לחץ על כפתור ה-**Copy** בפינה:

```
# FinanceApp — Real-Time Crypto & Stock Portfolio Simulator

A full-stack, real-time finance dashboard built with **Flask** and **PostgreSQL**. It combines a live Bitcoin data stream with anomaly detection, an interactive stock-trading simulator powered by live market prices, and automated daily portfolio tracking via AWS Lambda.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-AWS%20RDS-blue?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20EventBridge-232F3E?logo=amazon-aws&logoColor=white)

---

## 🚀 Key Features

* **⚡ Live Bitcoin Data Stream:** A background WebSocket client subscribes to the Binance ticker feed, persists every tick, and flags price anomalies using a rolling **z-score detector**.
* **📈 Stock Portfolio Simulator:** Real-time stock trading (powered by `yfinance`). Supports full user lifecycle: registration, authentication, buy/sell orders, real-time portfolio valuation, cash balance updates, and transaction logs.
* **📊 Technical Analysis Engine:** Calculates technical indicators for any stock symbol — including **SMA/EMA**, **RSI(14)**, **Rolling Volatility**, **Daily Returns**, and a **CUSUM Anomaly Detector**, all dynamically rendered using Chart.js.
* **🔒 Secure Per-User Sessions:** Password hashing via `werkzeug.security` with Flask session-based authentication to ensure complete user isolation.
* **☁️ Automated Daily Portfolio Snapshots (AWS Lambda):** A scheduled serverless function snapshots every user's total net worth daily, populating historical data for "value over time" performance tracking.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.11, Flask, Werkzeug |
| **Database** | PostgreSQL (AWS RDS in Production) |
| **Data Ingestion** | `websocket-client` (Binance API), `yfinance` |
| **Data Analysis** | NumPy, Pandas |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Chart.js |
| **Infrastructure** | Docker, Docker Compose, AWS Lambda, EventBridge |

---

## 📂 Project Structure

.
├── app.py                   # Main Flask application (routes, auth, WS thread)
├── common/
│   ├── DatabaseManager.py   # PostgreSQL operations & connection pooling
│   └── ring_buffer.py       # Fixed-size buffer for real-time anomaly detection
├── trading/
│   ├── portfolio.py         # Trading logic: buy, sell, holdings valuation
│   └── stock_client.py      # yfinance integration for market data
├── ingestion/
│   ├── websocket_client.py  # Binance WebSocket client
│   ├── anomaly_detector.py  # Rolling Z-Score detector algorithm
│   └── indicators.py        # Technical indicators (RSI, SMA, EMA, CUSUM)
├── templates/
│   ├── index.html           # Main dashboard interface
│   └── auth_modal.html      # Authentication modal UI
├── static/
│   ├── style.css            # Main application styling
│   └── auth.style.css       # Authentication module styling
├── lambda_aws.py            # AWS Lambda function for daily portfolio snapshots
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-container orchestrator
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template

---

## ⚡ Getting Started

### Prerequisites
* **Docker & Docker Compose** *(Recommended)*, or
* **Python 3.11+** and a running **PostgreSQL** instance.

---

### Installation & Run

#### Option 1: Running with Docker (Recommended)

1. **Clone the repository & create environment file:**
   cp .env.example .env

2. **Generate a secret key for Flask:**
   python -c "import secrets; print(secrets.token_hex(32))"
   *(Paste the generated key into your .env file under FLASK_SECRET_KEY)*

3. **Build and launch the containers:**
   docker-compose up --build

4. **Access the dashboard at:** http://localhost:5000

---

#### Option 2: Running Locally (Without Docker)

1. **Setup Virtual Environment:**
   python -m venv venv
   source venv/bin/activate  *(On Windows: venv\Scripts\activate)*

2. **Install Dependencies:**
   pip install -r requirements.txt

3. **Configure Database:**
   Ensure your .env file points to an active PostgreSQL database instance.

4. **Start Application:**
   python app.py

---

## ⚙️ Environment Variables

| Variable | Description | Example |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | Secret key for session encryption *(Required)* | `f83a...91c2` *(64 hex chars)* |
| `FLASK_DEBUG` | Enable/Disable debug mode | `false` |
| `PORT` | Application port | `5000` |
| `DB_HOST` | Database host endpoint *(Required)* | `db` or `your-rds.amazonaws.com` |
| `DB_NAME` | Database name | `postgres` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASS` | Database password *(Required)* | `your_secure_password` |
| `DB_PORT` | PostgreSQL port | `5432` |

---

## 📡 API Reference

### Public Routes
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Dashboard interface |
| `GET` | `/trading/health` | Health check route |
| `POST` | `/register` | Register a new user |
| `POST` | `/login` | Authenticate user |
| `POST` | `/logout` | End current session |
| `GET` | `/trading/ticks/latest` | Get recent Bitcoin tick data |
| `GET` | `/trading/anomalies` | Get detected price anomalies |
| `POST` | `/trading/stock/analyze` | Run technical analysis on a symbol |

### Authenticated Routes *(Requires Session)*
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/trading/portfolio/trades` | Execute Buy/Sell trade |
| `GET` | `/trading/portfolio/balance` | Retrieve current cash balance |
| `GET` | `/trading/portfolio/holdings` | Retrieve active stock holdings |
| `GET` | `/trading/portfolio/history` | Get user transaction history |
| `GET` | `/trading/portfolio/value_history` | Retrieve historical valuation data |
| `GET` | `/trading/total_worth` | Get live portfolio total market value |

---

## ☁️ AWS Lambda Integration

`lambda_aws.py` functions as an automated daily CRON job triggerable via **Amazon EventBridge**.

* **Logic:** Calculates `Total Value = Cash + Sum(Holdings * Live Price)` for each user and stores a snapshot in `portfolio_value_history`.
* **Runtime Specs:** Python 3.11, `x86_64` architecture. Uses standard `urllib` for lightweight zero-dependency external fetching.
* **Network Setup:** If deployed inside a VPC to access a private RDS, ensure a NAT Gateway is configured; otherwise, deploy outside VPC and restrict RDS via Security Groups.

---

## 🛡️ Security Measures

* **Zero Hardcoded Credentials:** All passwords, keys, and endpoints are pulled dynamically from runtime environment variables.
* **Password Hashing:** Hashes stored using `pbkdf2:sha256` via Werkzeug.
* **Database Isolation:** PostgreSQL access rules restricted exclusively to trusted application subnets.

---

## 🔮 Roadmap / Future Improvements

- [ ] Decouple Binance WebSocket stream into a standalone background service.
- [ ] Implement data aggregation/tick throttling to optimize database storage.
- [ ] Add unit testing coverage using `pytest` for technical indicators and trading logic.

```
