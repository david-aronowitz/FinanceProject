FinanceApp — Real-Time Crypto & Stock Portfolio Simulator
A full-stack finance dashboard built with Flask and PostgreSQL. It combines a live Bitcoin data stream with anomaly detection, a stock-trading simulator powered by real market prices, and a daily AWS Lambda job that tracks each user's portfolio value over time.

Features
Live Bitcoin stream — a background WebSocket client subscribes to the Binance ticker feed, stores every tick, and flags price anomalies using a rolling z-score detector.
Stock portfolio simulator — register, log in, and buy/sell stocks at live prices (via yfinance). Cash balance, holdings, average buy price, and transaction history are all persisted.
Technical analysis — for any symbol the app computes SMA/EMA, RSI(14), rolling volatility, daily returns, and a CUSUM anomaly detector, all rendered as charts (Chart.js).
Per-user sessions — password hashing (werkzeug.security) and Flask session-based authentication, so each user only sees their own portfolio.
Daily value tracking (AWS Lambda) — a scheduled Lambda snapshots every user's total portfolio value into the database, powering a "value over time" chart once enough history exists.
Tech Stack
Layer	Technology
Backend	Python 3.11, Flask
Database	PostgreSQL (AWS RDS in production)
Data ingestion	websocket-client (Binance), yfinance (stocks)
Analysis	NumPy, Pandas
Frontend	HTML, CSS, vanilla JS, Chart.js
Infrastructure	Docker, docker-compose, AWS Lambda + EventBridge
Project Structure
.
├── app.py                     # Flask app: routes, auth, background WebSocket thread
├── common/
│   ├── DatabaseManager.py      # All PostgreSQL access (tables, reads, writes)
│   └── ring_buffer.py          # Fixed-size buffer used by the anomaly detector
├── trading/
│   ├── portfolio.py            # Portfolio model: buy / sell / valuation
│   └── stock_client.py         # Live stock prices via yfinance
├── ingestion/
│   ├── websocket_client.py     # Binance WebSocket -> DB + anomaly detection
│   ├── anomaly_detector.py     # Rolling z-score anomaly detection
│   └── indicators.py           # RSI, SMA/EMA, volatility, CUSUM, returns
├── templates/
│   ├── index.html              # Dashboard UI
│   └── auth_modal.html         # Login / register modal
├── static/
│   ├── style.css
│   └── auth.style.css
├── lambda_aws.py               # AWS Lambda: daily portfolio-value snapshot
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example                # Template for environment variables
└── .gitignore
Getting Started
Prerequisites
Docker & Docker Compose (recommended), or
Python 3.11 and a local/remote PostgreSQL instance.
1. Configure environment variables
Copy the template and fill in real values:

bash
cp .env.example .env
Generate a strong Flask secret key:

bash
python -c "import secrets; print(secrets.token_hex(32))"
Never commit .env. It is already listed in .gitignore.

2. Run with Docker (recommended)
This starts a local PostgreSQL container and the app together:

bash
docker-compose up --build
The app is then available at http://localhost:5000.

3. Run locally without Docker
bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
Make sure the DB_* variables in .env point to a reachable PostgreSQL instance.

Environment Variables
Variable	Description	Example
FLASK_SECRET_KEY	Secret key for signing session cookies (required)	a1b2c3... (64 chars)
FLASK_DEBUG	Enable Flask debug mode	false
PORT	Port the app listens on	5000
DB_HOST	PostgreSQL host (required)	db / RDS endpoint
DB_NAME	Database name	postgres
DB_USER	Database user	postgres
DB_PASS	Database password (required)	your-password
DB_PORT	Database port	5432
API Overview
Method	Endpoint	Auth	Description
GET	/	–	Dashboard page
GET	/trading/health	–	Health check
POST	/register	–	Create a new user
POST	/login	–	Log in (starts a session)
POST	/logout	–	Log out
GET	/trading/ticks/latest	–	Latest Bitcoin ticks
GET	/trading/anomalies	–	Recent price anomalies
POST	/trading/stock/analyze	–	Technical analysis for a symbol
POST	/trading/portfolio/trades	✔	Buy / sell a stock
GET	/trading/portfolio/balance	✔	Cash balance
GET	/trading/portfolio/holdings	✔	Current holdings
GET	/trading/portfolio/history	✔	Recent transactions
GET	/trading/portfolio/value_history	✔	Portfolio value over time (for the chart)
GET	/trading/total_worth	✔	Total portfolio value at live prices
AWS Lambda — Daily Portfolio Snapshot
lambda_aws.py runs on a schedule and, for every user, computes cash + (holdings × current price) and inserts the result into the portfolio_value_history table. The dashboard then renders a value-over-time chart once at least 10 data points exist.

Deployment notes

Handler: lambda_aws.lambda_handler
Runtime: Python 3.11, architecture x86_64 (the bundled psycopg2 binary is built for this target).
Environment variables: same DB_* values as the app.
Schedule: an EventBridge Scheduler rule (e.g. daily at 11:00 Asia/Jerusalem).
Internet access: the function fetches live prices from Yahoo Finance using only the Python standard library (urllib), so no extra dependencies are needed — but it must be able to reach the internet. If the Lambda runs inside a VPC to reach a private RDS, it needs a NAT Gateway; otherwise keep it outside a VPC with a publicly-accessible RDS restricted by security group.
Security
All secrets (DB credentials, Flask key) are read from environment variables — nothing sensitive is hard-coded.
.env is git-ignored; use .env.example as the shared template.
Passwords are stored hashed, never in plain text.
Restrict the RDS security group to trusted IPs — never 0.0.0.0/0.
Possible Future Improvements
Run the Binance ingestion as its own service/process rather than a thread inside the web app.
Throttle tick storage (store aggregates instead of every tick) to limit database growth.
Add automated tests for the portfolio and analysis logic.

