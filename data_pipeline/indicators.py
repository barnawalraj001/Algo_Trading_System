# data_pipeline/indicators.py

import pandas as pd
import ta

def calculate_indicators(data):
    """
    Calculates all required technical indicators (RSI, 20-DMA, 50-DMA).

    Args:
        data (pd.DataFrame): DataFrame with stock data. Must have a 'Close' column.

    Returns:
        pd.DataFrame: The DataFrame with added indicator columns.
    """
    if data is None or 'Close' not in data.columns:
        print("Error: Input data is invalid or missing 'Close' column.")
        return None

    # Using direct functional calls from 'ta' to avoid potential version compatibility issues.
    # Calculate RSI (14-day)
    data['RSI'] = ta.momentum.rsi(close=data['Close'], window=14) # type: ignore

    # Calculate 20-day Moving Average
    data['SMA_20'] = data['Close'].rolling(window=20).mean()

    # Calculate 50-day Moving Average
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    
    print("Calculated RSI, 20-DMA, and 50-DMA.")
    return data

if __name__ == '__main__':
    # Example Usage (requires fetch_data.py to be in the same directory)
    from fetch_data import fetch_stock_data
    
    print("--- Testing indicators.py ---")
    sample_ticker = 'INFY.NS'
    stock_data = fetch_stock_data(sample_ticker)
    
    if stock_data is not None:
        stock_data_with_indicators = calculate_indicators(stock_data)
        if stock_data_with_indicators is not None:
            print(f"\nData with indicators for {sample_ticker} (last 5 days):")
            # Show relevant columns
            print(stock_data_with_indicators[['Close', 'RSI', 'SMA_20', 'SMA_50']].tail()) 