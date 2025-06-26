# data_pipeline/google_sheets_logger.py

import os
import gspread
import pandas as pd
from typing import List, Dict, Any
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv

# --- README Snippet ---
"""
How to set up Google Sheets API access:

1.  Create a new project in the Google Cloud Console (https://console.cloud.google.com/).
2.  Enable the "Google Drive API" and "Google Sheets API" for your project.
3.  Create a Service Account:
    - Go to "Credentials" -> "Create Credentials" -> "Service Account".
    - Give it a name (e.g., "algo-trading-bot").
    - Grant it the "Editor" role to allow it to modify Google Sheets.
4.  Create a JSON key for the Service Account:
    - After creating the account, go to its "Keys" tab -> "Add Key" -> "Create new key".
    - Choose "JSON" and download the file. Rename it to `credentials.json`.
5.  Create a `.env` file in the project root with the following content:
    
    GOOGLE_CREDENTIALS_PATH="path/to/your/credentials.json"
    GOOGLE_SHEET_NAME="AlgoTrading-Log"

6.  Share your Google Sheet:
    - Open the `credentials.json` file and find the `client_email` address.
    - In your Google Sheet, click "Share" and paste this email, giving it "Editor" permissions.
"""

# Load environment variables from .env file
load_dotenv()

def _get_gspread_client():
    """Authenticates with Google and returns a gspread client instance."""
    try:
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if not creds_path or not os.path.exists(creds_path):
            print("Error: GOOGLE_CREDENTIALS_PATH is not set in .env or the file does not exist.")
            return None
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope) # type: ignore
        client = gspread.authorize(creds) # type: ignore
        return client
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

def _get_or_create_worksheet(spreadsheet, title):
    """Gets a worksheet by title, creating it if it doesn't exist."""
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        print(f"Worksheet '{title}' not found. Creating it.")
        return spreadsheet.add_worksheet(title=title, rows="1000", cols="20")

def log_trade_signals(signals_data: List[Dict[str, Any]]):
    """Appends daily signal checks to the 'Trade Signals' tab."""
    # Get the gspread client and sheet name from environment variables
    client = _get_gspread_client()
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not client or not sheet_name or not signals_data:
        print("Client, sheet name, or signals data is missing. Skipping signal logging.")
        return

    try:
        # Open the spreadsheet and the specific worksheet
        spreadsheet = client.open(sheet_name)
        worksheet = _get_or_create_worksheet(spreadsheet, "Trade Signals")
        
        # Get header row to see if we need to add it
        header = ["Date", "Stock", "RSI", "SMA_20", "SMA_50", "Signal"]
        if not worksheet.get_all_values(): # Check if sheet is empty
            worksheet.append_row(header)

        # Convert list of dictionaries to a list of lists for appending
        rows_to_append = [
            [
                signal.get("Date"),
                signal.get("Stock"),
                f"{signal.get('RSI', 0):.2f}",
                f"{signal.get('SMA_20', 0):.2f}",
                f"{signal.get('SMA_50', 0):.2f}",
                "Yes" if signal.get("Signal") else "No"
            ] for signal in signals_data
        ]
        
        # Append all new signal rows in a single API call
        worksheet.append_rows(rows_to_append)
        print(f"Successfully appended {len(rows_to_append)} rows to 'Trade Signals'.")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet '{sheet_name}' not found. Please create it and share it.")
    except Exception as e:
        print(f"An error occurred while logging trade signals: {e}")

def log_backtest_results(trades_df: pd.DataFrame):
    """Writes the full backtest trade log to the 'Backtest Log' tab."""
    client = _get_gspread_client()
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not client or not sheet_name:
        return

    try:
        spreadsheet = client.open(sheet_name)
        worksheet = _get_or_create_worksheet(spreadsheet, "Backtest Log")
        worksheet.clear()  # Clear old data
        set_with_dataframe(worksheet, trades_df)
        print("Successfully logged backtest results to 'Backtest Log'.")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet '{sheet_name}' not found. Please create it and share it.")
    except Exception as e:
        print(f"An error occurred while logging backtest results: {e}")

def log_summary_stats(stats: Dict[str, Any]):
    """Updates the 'Summary' tab with key backtest statistics."""
    client = _get_gspread_client()
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not client or not sheet_name:
        return

    try:
        spreadsheet = client.open(sheet_name)
        worksheet = _get_or_create_worksheet(spreadsheet, "Summary")
        
        # Prepare data for batch update
        update_data = [
            ["Metric", "Value"],
            ["Total Trades", stats.get('total_trades', 'N/A')],
            ["Win Ratio", stats.get('win_ratio', 'N/A')],
            ["Average Return", stats.get('avg_return', 'N/A')]
        ]
        
        worksheet.update('A1', update_data) # type: ignore
        print("Successfully logged summary stats to 'Summary'.")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet '{sheet_name}' not found.")
    except Exception as e:
        print(f"An error occurred while logging summary stats: {e}")

if __name__ == '__main__':
    print("--- Testing google_sheets_logger.py ---")
    print("This script requires a valid .env file and credentials to run.")
    
    # Create dummy data for testing
    dummy_df = pd.DataFrame({
        'Stock': ['TEST.NS'], 'Buy Date': ['2023-01-01'], 'Buy Price': [100],
        'Sell Date': ['2023-01-06'], 'Sell Price': [105], 'Return (%)': [5.0], 'Status': ['Win']
    })
    dummy_stats = {'total_trades': 1, 'win_ratio': '100.00%', 'avg_return': '5.00%'}
    dummy_signals = [{
        'Date': '2023-01-01', 'Stock': 'TEST.NS', 'RSI': 25, 
        'SMA_20': 101, 'SMA_50': 100, 'Signal': True
    }]

    print("\nAttempting to log dummy trade signals...")
    log_trade_signals(dummy_signals)

    print("\nAttempting to log dummy backtest results...")
    log_backtest_results(dummy_df)
    
    print("\nAttempting to log dummy summary stats...")
    log_summary_stats(dummy_stats)
    
    print("\n--- Test Complete ---")
    print("Check your Google Sheet 'AlgoTrading-Log' for the new tabs and data.") 