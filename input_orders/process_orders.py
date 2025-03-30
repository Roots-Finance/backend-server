import pandas as pd

def insert_buy_order(portfolio, date, ticker, shares, price_Per_Share, start_date, end_date):
    # Adding another stock (example: JPM)
    print("\n\nADDING ANOTHER STOCK")
    print("==============================")
    data_route = f'stockdata/{ticker}.csv'
    df = pd.read_csv(data_route)
    df['Date'] = pd.to_datetime(df['Date'])
    
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    temp_df = df.loc[mask, ['Date', 'Close']]
    
    # Compute daily return for temp_df
    temp_df['Daily Return'] = temp_df['Close'] / temp_df['Close'].iloc[0]
    temp_df.set_index('Date', inplace=True)  # Only call this once
    
    # Calculate the initial value for the stock
    start_val = shares * price_Per_Share    
    
    # Add the stock's performance to the portfolio DataFrame
    portfolio[ticker] = start_val * temp_df['Daily Return']

    # Prepend 0's before the buy order
    # Convert the order date to a datetime object
    order_date = pd.to_datetime(date)
    # Set the performance values before the order date to 0
    portfolio.loc[portfolio.index < order_date, ticker] = 0

    print("And portfolio looks like:")
    return portfolio

def insert_sell_order(portfolio, date, ticker, shares, price_Per_Share, start_date, end_date):
    print("\n\nPROCESSING SELL ORDER")
    print("==============================")
    
    # Convert the sell order date to a datetime object.
    order_date = pd.to_datetime(date)
    
    # Calculate the sale value.
    sell_amount = shares * price_Per_Share

    # Ensure that the ticker exists in the portfolio.
    if ticker not in portfolio.columns:
        raise ValueError(f"Ticker {ticker} not found in portfolio. Cannot process sell order.")

    # Subtract the sell amount from the existing ticker column on and after the order date.
    portfolio.loc[portfolio.index >= order_date, ticker] -= sell_amount
    
    print("Updated portfolio looks like:")
    return portfolio

def main():
    # Read the orders CSV file
    orders = pd.read_csv('input_orders/orders.csv')
    print(f"Orders Form: \n{orders.head()}\n")
    
    # Pull the start date from the orders DataFrame
    start_date = orders['Date'][0]
    end_date = '2025-03-29'
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Identify the first asset from the orders
    asset_one = orders['Ticker'][0]
    print("asset one:")
    print(asset_one)
    print("")
    
    # Identify all unique tickers
    unique_tickers = orders['Ticker'].unique().tolist()
    
    # Pull data for the first ticker (example: AAPL) over the date range
    df = pd.read_csv('stockdata/AAPL.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_close = df.loc[mask, ['Date', 'Close']]
    # Compute daily return relative to the first day's close
    filtered_close['Daily Return'] = filtered_close['Close'] / filtered_close['Close'].iloc[0]
    
    print(filtered_close.head())
    print("\n\n")
    
    # Calculate the initial value for the first asset
    start_val = orders['Shares'][0] * orders['Price_Per_Share'][0]
    
    # Create the portfolio DataFrame with the first asset's performance
    portfolio = pd.DataFrame({
        'Date': filtered_close['Date'],
        asset_one: start_val * filtered_close['Daily Return']
    })
    
    # Set the Date column as the index for the portfolio DataFrame
    portfolio.set_index('Date', inplace=True)
    print(portfolio)

    print("\nMain run successful, now moving onto new stock")
    # Adding another stock
    updated_port = insert_buy_order(portfolio, '2025-01-06', ticker='JPM', shares=50, price_Per_Share=240.85,start_date=start_date, end_date=end_date)
    print(portfolio)

    updated_port = insert_sell_order(portfolio, '2025-01-13', ticker='AAPL', shares=25, price_Per_Share=233.53,start_date=start_date, end_date=end_date)
    print(updated_port)
    print("\nPrev run successful, now moving onto new stock")

    updated_port = insert_buy_order(portfolio, '2025-01-24', ticker='NFLX', shares=20, price_Per_Share=300.30,start_date=start_date, end_date=end_date)
    print(updated_port)
    print("\nPrev run successful, now moving onto new stock")

    updated_port = insert_sell_order(portfolio, '2025-02-04', ticker='NFLX', shares=20, price_Per_Share=290.20,start_date=start_date, end_date=end_date)
    print(updated_port)
    print("\nPrev run successful, now moving onto new stock")


if __name__ == '__main__':
    main()
