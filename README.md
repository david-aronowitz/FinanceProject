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

```text
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
