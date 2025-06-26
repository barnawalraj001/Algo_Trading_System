# Algo Trading System

A modular, end-to-end algo-trading system for NIFTY 50 stocks, featuring rule-based and machine learning strategies, automated backtesting, and Google Sheets integration for trade logging and reporting.

---

## 📈 Project Overview
This project is a Python-based trading system that:
- Implements a rule-based trading strategy (RSI + moving average crossover)
- Backtests the strategy and logs results
- Optionally uses machine learning to predict next-day price movement
- send alerts through bot to telegram
- Logs all signals, trades, and summaries to Google Sheets for easy tracking

---

## 🚀 Features & Deliverables

### 1. Data Ingestion
- Fetches daily historical data for at least 3 NIFTY 50 stocks (e.g., RELIANCE.NS, INFY.NS, TCS.NS)
- Uses [yfinance](https://github.com/ranaroussi/yfinance) for free data

### 2. Trading Strategy Logic
- Buy signal: RSI < 30
- Confirmed by: 20-day moving average (DMA) crossing above 50-DMA
- Modular code for indicator calculation and signal logic

### 3. Backtesting
- Backtests the strategy over the last 6 months (or more)
- Logs each trade: date, buy/sell price, return %, win/loss
- Computes total trades, win ratio, and average return

### 4. ML Automation (Bonus)
- Trains a Logistic Regression model to predict next-day movement using RSI, MACD, and Volume
- Outputs accuracy, confusion matrix, and classification report
- ML is optional and for research only working on only Reliance.NS data only

### 5. Google Sheets Automation
- Logs trade signals, backtest logs, and summary stats to a Google Sheet
- Uses `gspread` and `oauth2client` for API access
- Tabs: Trade Signals, Backtest Log, Summary

### 6. Algo Component
- Main script can be scheduled or run on demand
- Supports multiple modes: live, backtest, ml
- All results are logged and printed

### 7. Code Quality
- Modular Python code (one module per concern)
- Logging and error handling throughout
- Extensive comments and docstrings

---

## 🗂️ Project Structure

```
Algo Trading System/
│
├── data_pipeline/
│   ├── fetch_data.py           # Fetches stock data from yfinance
│   ├── indicators.py           # Calculates RSI, moving averages, etc.
│   ├── signal_logic.py         # Implements buy signal logic
│   ├── backtest.py             # Backtesting engine
│   ├── google_sheets_logger.py # Google Sheets logging functions
│   ├── ml_model.ipynb          # ML model for next-day prediction and for sending alert msg by telegram bot
│   └── main.py                 # Main orchestrator script
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Ignore sensitive files and cache
├── README.md                   # This file
└── .env.example                #  environment variables (not in repo)
```

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/algo-trading-system.git
   cd algo-trading-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Example:
     ```env
     GOOGLE_CREDENTIALS_PATH="/path/to/your/credentials.json"
     GOOGLE_SHEET_NAME="AlgoTrading-Log"
     TELEGRAM_BOT_TOKEN= Tke token id of your telegram bot
     TELEGRAM_CHAT_ID= Fetch chat id too of that bot
     ```

4. **Google Sheets Setup:**
   - Create a Google Cloud project and enable Sheets/Drive API
   - Create a service account and download `credentials.json`
   - Share your Google Sheet with the service account email
   - See `google_sheets_logger.py` docstring for full instructions

---

## 🏃‍♂️ Usage

### Run the main script in different modes:

- **Live Mode (default):**
  ```bash
  python data_pipeline/main.py --mode live
  ```
  - Checks latest buy signals for all stocks and logs to Google Sheets

- **Backtest Mode:**
  ```bash
  python data_pipeline/main.py --mode backtest
  ```
  - Runs a 6-month (or more) backtest, logs all trades and summary stats

- **ML Mode :**
  -ml_model.ipynb ; Run all the blocks of jupyter notebook
  - Trains and evaluates a Logistic Regression model for each stock (currently for Reliance.NS)
  - Prints accuracy, confusion matrix, and classification report
  - Send Alert message to telegram by bot  

---

## 📊 Google Sheets Logging
- All trade signals, backtest logs, and summary stats are automatically logged to your Google Sheet (`AlgoTrading-Log`)
- Tabs:
  - **Trade Signals:** Each live signal check
  - **Backtest Log:** All trades from backtesting
  - **Summary:** Total trades, win ratio, average return

---

## 🧩 Module Explanations
- **fetch_data.py:** Downloads historical stock data using yfinance
- **indicators.py:** Computes RSI, moving averages, and other indicators
- **signal_logic.py:** Implements the buy signal logic (RSI < 30 + 20/50 DMA crossover)
- **backtest.py:** Simulates the strategy, logs trades, and computes stats
- **google_sheets_logger.py:** Handles all Google Sheets API interactions
- **main.py:** Orchestrates the workflow, supports multiple modes
-**ml_model.ipynb:** For Now, we are using it to train the model on Reliance.NS data and to send alert by telegram bot

---

## 📝 Notes & Limitations
- ML model is for research/testing only; performance is poor due to limited features and data
- For real trading, use more robust data sources, risk management, and compliance checks
- All credentials and sensitive info should be kept in `.env` and `.gitignore`d

---

## 🤝 Contributing
- Fork the repo and create a feature branch
- Submit pull requests with clear descriptions
- Open issues for bugs or feature requests

---


 # Algo_Trading_System
