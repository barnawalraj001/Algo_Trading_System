# data_pipeline/backtest.py

import pandas as pd
from indicators import calculate_indicators

def run_backtest(stock_data: pd.DataFrame, ticker: str):
    """
    Runs a backtest on historical stock data based on a defined trading strategy.

    Strategy:
    - Buy Signal: RSI < 30 and 20-DMA crosses above 50-DMA.
    - Action: Buy at the next day's open price.
    - Exit: Sell 5 trading days later at the open price.

    Args:
        stock_data (pd.DataFrame): DataFrame with historical stock data.
        ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing backtest summary statistics and the trade log.
              Returns None if the backtest cannot be run.
    """
    if stock_data is None or stock_data.empty:
        print(f"No data provided for {ticker}, skipping backtest.")
        return None

    # Step 1: Calculate technical indicators
    data = calculate_indicators(stock_data.copy())
    data = data.dropna()

    if len(data) < 7: # Need at least 1 day for signal, 1 for buy, 5 for hold
        print(f"Not enough data for {ticker} to run a backtest after indicator calculation.")
        return None

    trades = []
    
    # Step 2: Loop through data to find trading signals
    # We loop up to the 6th to last day to ensure there's a sell date 5 days after buy
    for i in range(1, len(data) - 6):
        # Yesterday's and Today's data slices
        yesterday = data.iloc[i-1]
        today = data.iloc[i]

        # Signal Conditions
        rsi_signal = today['RSI'] < 30
        crossover_signal = (today['SMA_20'] > today['SMA_50']) and (yesterday['SMA_20'] <= yesterday['SMA_50'])

        if rsi_signal and crossover_signal:
            # Signal triggered, plan to buy next day
            buy_date = data.index[i+1]
            buy_price = data['Open'].iloc[i+1]
            
            # Plan to sell 5 days after buying
            sell_date = data.index[i+6]
            sell_price = data['Open'].iloc[i+6]
            
            # Calculate return
            pct_return = ((sell_price - buy_price) / buy_price) * 100
            
            # Log the trade
            trades.append({
                'Stock': ticker,
                'Buy Date': buy_date.strftime('%Y-%m-%d'),
                'Buy Price': buy_price,
                'Sell Date': sell_date.strftime('%Y-%m-%d'),
                'Sell Price': sell_price,
                'Return (%)': pct_return,
                'Status': 'Win' if pct_return > 0 else 'Loss'
            })

    if not trades:
        print(f"No trades were executed for {ticker} during the backtest period.")
        return {
            'total_trades': 0,
            'win_ratio': 0,
            'avg_return': 0,
            'trade_log': pd.DataFrame()
        }

    # Step 3: Analyze results
    trade_log_df = pd.DataFrame(trades)
    total_trades = len(trade_log_df)
    wins = len(trade_log_df[trade_log_df['Status'] == 'Win'])
    win_ratio = (wins / total_trades) * 100 if total_trades > 0 else 0
    avg_return = trade_log_df['Return (%)'].mean()
    
    summary = {
        'total_trades': total_trades,
        'win_ratio': f"{win_ratio:.2f}%",
        'avg_return': f"{avg_return:.2f}%",
        'trade_log': trade_log_df
    }
    
    return summary

if __name__ == '__main__':
    from fetch_data import fetch_stock_data
    
    print("--- Testing backtest.py ---")
    # Using a longer period to increase the chance of finding signals
    sample_ticker = 'RELIANCE.NS'
    stock_data = fetch_stock_data(sample_ticker, period="2y") 
    
    if stock_data is not None:
        backtest_results = run_backtest(stock_data, sample_ticker)
        if backtest_results:
            print(f"\nBacktest Results for {sample_ticker}:")
            print(f"  - Total Trades: {backtest_results['total_trades']}")
            print(f"  - Win Ratio: {backtest_results['win_ratio']}")
            print(f"  - Average Return: {backtest_results['avg_return']}")
            
            print("\n--- Trade Log ---")
            if not backtest_results['trade_log'].empty:
                print(backtest_results['trade_log'])
            else:
                print("No trades to display.")
            print("-----------------") 