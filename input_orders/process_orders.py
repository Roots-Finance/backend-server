import pandas as pd

def insert_buy_order(portfolio, date, ticker, shares, price_Per_Share, start_date, end_date):
    print("\n\nADDING BUY ORDER")
    print("==============================")
    data_route = f'stockdata/{ticker}.csv'
    df = pd.read_csv(data_route)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Convert order date to datetime and use it as the start for this ticker's data
    order_date = pd.to_datetime(date)
    
    # Filter the ticker's data starting at the order date (not the overall start_date)
    mask = (df['Date'] >= order_date) & (df['Date'] <= end_date)
    temp_df = df.loc[mask, ['Date', 'Close']]
    
    # Compute daily return relative to the close price on the order date
    base_close = temp_df['Close'].iloc[0]
    temp_df['Daily Return'] = temp_df['Close'] / base_close
    temp_df.set_index('Date', inplace=True)
    
    # Calculate the order’s initial value
    start_val = shares * price_Per_Share
    
    # Create a new series for the new order, initializing with zeros across the portfolio's index
    new_order_series = pd.Series(0, index=portfolio.index)
    new_order_series.loc[temp_df.index] = start_val * temp_df['Daily Return']
    
    # If the ticker already exists, add the new order's series to the existing values;
    # otherwise, simply assign the new series to that ticker.
    if ticker in portfolio.columns:
        portfolio[ticker] = portfolio[ticker].fillna(0) + new_order_series
    else:
        portfolio[ticker] = new_order_series
    
    print("Portfolio after BUY order:")
    return portfolio


def insert_sell_order(portfolio, date, ticker, shares, price_Per_Share, start_date, end_date):
    print("\n\nPROCESSING SELL ORDER")
    print("==============================")
    order_date = pd.to_datetime(date)
    sell_amount = shares * price_Per_Share

    # Make sure the ticker exists
    if ticker not in portfolio.columns:
        raise ValueError(f"Ticker {ticker} not found in portfolio. Cannot process sell order.")
    
    # Subtract the sell amount for every trading day on and after the sell date
    portfolio.loc[portfolio.index >= order_date, ticker] -= sell_amount
    
    print("Portfolio after SELL order:")
    return portfolio

def process_orders():
    # Read and clean orders CSV
    orders = pd.read_csv('input_orders/orders.csv')
    orders['Date'] = pd.to_datetime(orders['Date'])
    orders['Order_Type'] = orders['Order_Type'].str.strip().str.lower()
    orders['Ticker'] = orders['Ticker'].str.strip()
    
    orders.sort_values('Date', inplace=True)
    
    # Overall start and end dates
    start_date = orders['Date'].min()
    end_date = '2025-03-29'
    
    # Use the first order's ticker (assumed to be a buy) to build the portfolio index
    first_order = orders.iloc[0]
    first_ticker = first_order['Ticker']
    df_first = pd.read_csv(f'stockdata/{first_ticker}.csv')
    df_first['Date'] = pd.to_datetime(df_first['Date'])
    
    mask = (df_first['Date'] >= start_date) & (df_first['Date'] <= end_date)
    filtered_close = df_first.loc[mask, ['Date', 'Close']]
    filtered_close['Daily Return'] = filtered_close['Close'] / filtered_close['Close'].iloc[0]
    
    # Create portfolio using only the dates when the market was open (from the first ticker's CSV)
    portfolio = pd.DataFrame({
        'Date': filtered_close['Date'],
        first_ticker: first_order['Shares'] * first_order['Price_Per_Share'] * filtered_close['Daily Return']
    })
    portfolio.set_index('Date', inplace=True)
    
    print("Initial portfolio based on first order:")
    print(portfolio)
    
    # Process subsequent orders (starting from index 1)
    for idx, order in orders.iloc[1:].iterrows():
        order_date = order['Date']
        order_type = order['Order_Type']
        ticker = order['Ticker']
        shares = order['Shares']
        price = order['Price_Per_Share']
        
        print(f"\nProcessing order {idx}: {order_type.upper()} {ticker} on {order_date.date()}")
        
        if order_type == "buy":
            portfolio = insert_buy_order(portfolio, order_date, ticker, shares, price, start_date, end_date)
        elif order_type == "sell":
            portfolio = insert_sell_order(portfolio, order_date, ticker, shares, price, start_date, end_date)
        else:
            print(f"Unrecognized order type: {order_type}")
        
        print("\nPortfolio snapshot after processing order:")
        print(portfolio)
    
    return portfolio

def main():
    final_portfolio = process_orders()
    final_portfolio['total'] = final_portfolio.sum(axis=1)

    print("\nFinal portfolio:")
    print(final_portfolio)
    # YOU'D RETURN final_portfolio!!!!

if __name__ == '__main__':
    main()
