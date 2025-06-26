# data_pipeline/fetch_data.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(ticker, period="6mo"):
    """
    Fetches daily historical stock data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'RELIANCE.NS').
        period (str): The period to fetch data for (e.g., "6mo", "1y").

    Returns:
        pd.DataFrame: A DataFrame containing the historical stock data,
                      or None if data could not be fetched.
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch historical data for the last 6 months
        data = stock.history(period=period, auto_adjust=True)
        if data.empty:
            print(f"No data found for ticker {ticker}. It might be delisted or an invalid ticker.")
            return None
        print(f"Successfully fetched data for {ticker}")
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    print("--- Testing fetch_data.py ---")
    reliance_data = fetch_stock_data('RELIANCE.NS')
    if reliance_data is not None:
        print("\nReliance Data Sample:")
        print(reliance_data.head()) 