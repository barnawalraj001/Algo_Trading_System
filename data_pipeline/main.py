# data_pipeline/main.py

import argparse
import pandas as pd
from datetime import datetime

# Import all necessary functions from our modules
from fetch_data import fetch_stock_data
from indicators import calculate_indicators
from signal_logic import check_buy_signal
from backtest import run_backtest
from google_sheets_logger import log_trade_signals, log_backtest_results, log_summary_stats

def main():
    """
    Main function to drive the algo-trading analysis.
    It can be run in two modes: 'live' or 'backtest'.
    
    - live: Checks for the latest buy signal for a list of stocks and logs it.
    - backtest: Runs a historical simulation of the trading strategy and logs the results.
    """
    # --- Command-Line Argument Parsing ---
    # Sets up a parser to accept command-line arguments.
    # This allows the user to choose the execution mode.
    parser = argparse.ArgumentParser(description="Algo-Trading Analysis Tool")
    parser.add_argument(
        '--mode', 
        type=str, 
        default='live', 
        choices=['live', 'backtest'],
        help="The mode to run the script in: 'live' for latest signal check, 'backtest' for historical simulation."
    )
    args = parser.parse_args()

    # --- Stock Universe Definition ---
    # Define the list of NIFTY 50 stocks we want to analyze.
    nifty_50_stocks = ['RELIANCE.NS', 'INFY.NS', 'TCS.NS']

    # --- Mode Execution Logic ---
    if args.mode == 'live':
        # --- Live Mode ---
        # Checks for the most recent trading signal and logs it.
        print("--- Running in LIVE mode ---")
        live_signals_to_log = []

        for stock_ticker in nifty_50_stocks:
            print(f"\n----- Analyzing {stock_ticker} for Live Signal -----")
            
            # Step 1: Fetch the last 6 months of data for indicator calculation.
            stock_data = fetch_stock_data(stock_ticker, period="6mo")
            if stock_data is None:
                continue
                
            # Step 2: Calculate technical indicators.
            data_with_indicators = calculate_indicators(stock_data)
            if data_with_indicators is None:
                continue

            # Step 3: Check for a buy signal based on the latest data.
            signal, rsi, sma20, sma50 = check_buy_signal(data_with_indicators)

            # Step 4: Print the summary to the console.
            print("\n--- Live Signal Summary ---")
            if rsi is not None:
                print(f"  - Latest RSI: {rsi:.2f}")
                print(f"  - 20-Day MA: {sma20:.2f}")
                print(f"  - 50-Day MA: {sma50:.2f}")
                print(f"  - Buy Signal Triggered: {'Yes' if signal else 'No'}")

                # Prepare data for logging to Google Sheets
                live_signals_to_log.append({
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Stock": stock_ticker,
                    "RSI": rsi,
                    "SMA_20": sma20,
                    "SMA_50": sma50,
                    "Signal": signal
                })
            else:
                print("  - Could not determine signal due to insufficient data.")
            print("---------------------------")

        # Step 5: Log all collected signals to Google Sheets.
        if live_signals_to_log:
            print("\nLogging live signals to Google Sheets...")
            log_trade_signals(live_signals_to_log)

    elif args.mode == 'backtest':
        # --- Backtest Mode ---
        # Simulates the strategy over historical data and logs performance.
        print("--- Running in BACKTEST mode ---")
        all_trades = []
        
        for stock_ticker in nifty_50_stocks:
            print(f"\n----- Backtesting {stock_ticker} -----")
            # For backtesting, a longer period like 2 years is often better to get more trades.
            stock_data = fetch_stock_data(stock_ticker, period="2y")
            
            # Run the backtest function which handles its own indicator calculations.
            results = run_backtest(stock_data, stock_ticker) # type: ignore
            
            if results and not results['trade_log'].empty:
                print(f"Backtest for {stock_ticker} generated {results['total_trades']} trades.")
                all_trades.append(results['trade_log'])
            else:
                print(f"No trades were generated for {stock_ticker} in the backtest.")

        # --- Aggregate and Log Backtest Results ---
        if all_trades:
            # Combine all individual trade logs into one master DataFrame.
            combined_trade_log = pd.concat(all_trades, ignore_index=True)
            
            # Calculate overall performance statistics.
            total_trades = len(combined_trade_log)
            wins = len(combined_trade_log[combined_trade_log['Status'] == 'Win'])
            win_ratio = (wins / total_trades) * 100 if total_trades > 0 else 0
            avg_return = combined_trade_log['Return (%)'].mean()
            
            # Prepare the summary dictionary.
            overall_summary = {
                'total_trades': total_trades,
                'win_ratio': f"{win_ratio:.2f}%",
                'avg_return': f"{avg_return:.2f}%"
            }
            
            # Print the final summary to the console.
            print("\n--- Overall Backtest Summary ---")
            print(f"  - Total Trades: {overall_summary['total_trades']}")
            print(f"  - Win Ratio: {overall_summary['win_ratio']}")
            print(f"  - Average Return: {overall_summary['avg_return']}")
            print("--------------------------------")

            # Log the detailed trade log and the final summary to Google Sheets.
            print("\nLogging backtest results to Google Sheets...")
            log_backtest_results(combined_trade_log)
            log_summary_stats(overall_summary)
        else:
            print("\nNo trades were generated across all stocks. Nothing to log.")

    print("\n--- Analysis Complete ---")

if __name__ == "__main__":
    # This is the entry point of the script. It calls the main function.
    main() 