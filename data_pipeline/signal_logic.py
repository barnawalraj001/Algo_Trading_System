# data_pipeline/signal_logic.py

import pandas as pd

def check_buy_signal(data):
    """
    Checks for a buy signal based on RSI and moving average crossover.

    The buy signal conditions are:
    1. The latest RSI is less than 30.
    2. The 20-day Moving Average (20-DMA) has just crossed above the 50-day Moving Average (50-DMA).
       - This means 20-DMA > 50-DMA today.
       - And 20-DMA <= 50-DMA yesterday.

    Args:
        data (pd.DataFrame): DataFrame with stock data and indicator columns
                             ('RSI', 'SMA_20', 'SMA_50').

    Returns:
        tuple: A tuple containing:
            - bool: True if a buy signal is triggered, False otherwise.
            - float: The latest RSI value.
            - float: The latest 20-DMA value.
            - float: The latest 50-DMA value.
    """
    if data is None or not all(k in data.columns for k in ['RSI', 'SMA_20', 'SMA_50']):
        print("Error: DataFrame is missing required indicator columns.")
        return False, None, None, None
    
    # Drop rows with NaN values that result from indicator calculations
    data = data.dropna()

    # Ensure there's enough data for comparison after dropping NaNs
    if len(data) < 2:
        print("Not enough data to check for a signal after cleaning.")
        return False, None, None, None

    # Get the last two rows of data
    latest_data = data.iloc[-1]
    previous_data = data.iloc[-2]

    # Latest indicator values
    latest_rsi = latest_data['RSI']
    latest_sma_20 = latest_data['SMA_20']
    latest_sma_50 = latest_data['SMA_50']

    # Condition 1: RSI is below 30
    rsi_condition = latest_rsi < 30
    
    # Condition 2: 20-DMA crosses above 50-DMA
    crossover_condition = (latest_sma_20 > latest_sma_50) and \
                          (previous_data['SMA_20'] <= previous_data['SMA_50'])

    # Check if both conditions are met
    buy_signal = rsi_condition and crossover_condition
    
    print(f"Checking signal: RSI<30 ({rsi_condition}), 20/50 DMA Crossover ({crossover_condition})")

    return buy_signal, latest_rsi, latest_sma_20, latest_sma_50


if __name__ == '__main__':
    # Example Usage (requires fetch_data and indicators)
    from fetch_data import fetch_stock_data
    from indicators import calculate_indicators

    print("--- Testing signal_logic.py ---")
    sample_ticker = 'TCS.NS'
    stock_data = fetch_stock_data(sample_ticker)

    if stock_data is not None:
        stock_data_with_indicators = calculate_indicators(stock_data)
        
        if stock_data_with_indicators is not None:
            signal, rsi, sma20, sma50 = check_buy_signal(stock_data_with_indicators)

            print(f"\nSignal Check for {sample_ticker}:")
            if rsi is not None:
                print(f"  - Latest RSI: {rsi:.2f}")
                print(f"  - 20-DMA: {sma20:.2f}")
                print(f"  - 50-DMA: {sma50:.2f}")
                print(f"  - Buy Signal Triggered: {'Yes' if signal else 'No'}")
            else:
                print("Could not retrieve signal information.") 