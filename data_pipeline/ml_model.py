# data_pipeline/ml_model.py

import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


def run_ml_prediction(stock_symbol: str):
    """
    Trains and evaluates a Logistic Regression model to predict the next day's
    stock price movement (Up or Down) for a single stock.

    Args:
        stock_symbol (str): The stock ticker to run the analysis on (e.g., 'RELIANCE.NS').
    
    Returns:
        dict: Contains accuracy, classification report, confusion matrix, and stock symbol.
    """
    print(f"\n--- Running ML Prediction for {stock_symbol} ---")

    # Step 1: Fetch stock data
    try:
        raw_data = yf.download(stock_symbol, period="1y", auto_adjust=True)
        if raw_data.empty:
            print(f"No data found for {stock_symbol}.")
            return None
        print(f"Successfully fetched 1 year of data for {stock_symbol}.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    # Step 2: Build clean DataFrame for features
    close = raw_data['Close'].to_numpy().flatten()  # 1D array
    close_series = pd.Series(close, index=raw_data.index)
    volume = raw_data['Volume']  # 1D
    data = pd.DataFrame({
        'Close': close_series,
        'Volume': volume
    })

    # Step 3: Calculate technical indicators
    data['RSI'] = RSIIndicator(close=data['Close'], window=14).rsi()
    macd = MACD(close=data['Close'])
    data['MACD'] = macd.macd()

    # Step 4: Create target label (1 if next day's close is higher, else 0)
    data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Step 5: Drop rows with missing values
    data.dropna(inplace=True)
    if data.empty:
        print("Not enough data to train the model after cleaning. Skipping.")
        return None

    # Step 6: Select features and target
    features = ['RSI', 'MACD', 'Volume']
    X = data[features]
    y = data['Target']

    # Step 7: Split train/test (80/20, no shuffle for time series)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    print(f"Data split into training ({len(X_train)} rows) and testing ({len(X_test)} rows).")

    # Step 8: Train the Logistic Regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)
    print("Logistic Regression model trained successfully.")

    # Step 9: Predict and evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Down', 'Up'])
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Step 10: Print results
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("---------------------------------")

    return {
        'stock': stock_symbol,
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': conf_matrix
    }

def run_ml_for_multiple_stocks(stock_list):
    """
    Runs ML prediction for a list of stocks and prints summary for each.
    Args:
        stock_list (list): List of stock ticker symbols.
    """
    results = []
    for symbol in stock_list:
        res = run_ml_prediction(symbol)
        if res:
            results.append(res)
    print("\n=== ML Prediction Summary for All Stocks ===")
    for res in results:
        print(f"\nStock: {res['stock']}")
        print(f"Accuracy: {res['accuracy']:.4f}")
        print("Confusion Matrix:")
        print(res['confusion_matrix'])
    print("==========================================")

if __name__ == '__main__':
    print("--- Testing ml_model.py ---")
    # You can change or expand this list as needed
    test_tickers = ['RELIANCE.NS', 'INFY.NS', 'TCS.NS']
    run_ml_for_multiple_stocks(test_tickers)
