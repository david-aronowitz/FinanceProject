# FinanceApp — Real-Time Crypto & Stock Portfolio Simulator

A full-stack finance dashboard built with **Flask** and **PostgreSQL**. It combines a live Bitcoin data stream with anomaly detection, a stock-trading simulator powered by real market prices, and a daily AWS Lambda job that tracks each user's portfolio value over time.

---

## Features

* **Live Bitcoin stream** — A background WebSocket client subscribes to the Binance ticker feed, stores every tick, and flags price anomalies using a rolling z-score detector.
* **Stock portfolio simulator** — Register, log in, and buy/sell stocks at live prices (via `yfinance`). Cash balance, holdings, average buy price, and transaction history are all persisted.
* **Technical analysis** — For any symbol, the app computes SMA/EMA, RSI(14), rolling volatility, daily returns, and a CUSUM anomaly detector, all rendered as charts (`Chart.js`).
* **Per-user sessions** — Password hashing (`werkzeug.security`) and Flask session-based authentication, so each user only sees their own portfolio.
* **Daily value tracking (AWS Lambda)** — A scheduled Lambda snapshots every user's total portfolio value into the database, powering a "value over time" chart once enough history exists.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.11, Flask |
| **Database** | PostgreSQL (AWS RDS in production) |
| **Data ingestion** | `websocket-client` (Binance), `yfinance` (stocks) |
| **Analysis** | NumPy, Pandas |
| **Frontend** | HTML, CSS, vanilla JS, Chart.js |
| **Infrastructure** | Docker, docker-compose, AWS Lambda + EventBridge |

---

## Project Structure

```text
.
├── app.py                     # Flask app: routes, auth, background WebSocket thread
├── common/
│   ├── DatabaseManager.py     # All PostgreSQL access (tables, reads, writes)
│   └── ring_buffer.py         # Fixed-size buffer used by the anomaly detector
├── trading/
│   ├── portfolio.py           # Portfolio model: buy / sell / valuation
│   └── stock_client.py        # Live stock prices via yfinance
├── ingestion/
│   ├── websocket_client.py    # Binance WebSocket -> DB + anomaly detection
│   ├── anomaly_detector.py    # Rolling z-score anomaly detection
│   └── indicators.py          # RSI, SMA/EMA, volatility, CUSUM, returns
├── templates/
│   ├── index.html             # Dashboard UI
│   └── auth_modal.html        # Login / register modal
├── static/
│   ├── style.css
│   └── auth.style.css
├── lambda_aws.py              # AWS Lambda: daily portfolio-value snapshot
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example               # Template for environment variables
└── .gitignore
