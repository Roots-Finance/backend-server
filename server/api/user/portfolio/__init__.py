import base64
import json
import os

import pandas as pd
from dateutil.parser import parse
from flask import jsonify, request
from google import genai
from google.genai import types

from database import DB
from models import Account, Order, OrderType, Portfolio, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


def insert_buy_order(
    portfolio, date, ticker, shares, price_Per_Share, start_date, end_date
):
    data_route = f"stockdata/{ticker}.csv"
    df = pd.read_csv(data_route)
    df["Date"] = pd.to_datetime(df["Date"])

    # Convert order date to datetime and use it as the start for this ticker's data
    order_date = pd.to_datetime(date)

    # Filter the ticker's data starting at the order date (not the overall start_date)
    mask = (df["Date"] >= order_date) & (df["Date"] <= end_date)
    temp_df = df.loc[mask, ["Date", "Close"]]

    # Compute daily return relative to the close price on the order date
    base_close = temp_df["Close"].iloc[0]
    temp_df["Daily Return"] = temp_df["Close"] / base_close
    temp_df.set_index("Date", inplace=True)

    # Calculate the order’s initial value
    start_val = shares * price_Per_Share

    # Create a new series for the new order, initializing with zeros across the portfolio's index
    new_order_series = pd.Series(0, index=portfolio.index)
    new_order_series.loc[temp_df.index] = start_val * temp_df["Daily Return"]

    # If the ticker already exists, add the new order's series to the existing values;
    # otherwise, simply assign the new series to that ticker.
    if ticker in portfolio.columns:
        portfolio[ticker] = portfolio[ticker].fillna(0) + new_order_series
    else:
        portfolio[ticker] = new_order_series

    return portfolio


def insert_sell_order(
    portfolio, date, ticker, shares, price_Per_Share, start_date, end_date
):
    order_date = pd.to_datetime(date)
    sell_amount = shares * price_Per_Share

    # Make sure the ticker exists
    if ticker not in portfolio.columns:
        raise ValueError(
            f"Ticker {ticker} not found in portfolio. Cannot process sell order."
        )

    # Subtract the sell amount for every trading day on and after the sell date
    portfolio.loc[portfolio.index >= order_date, ticker] -= sell_amount

    return portfolio


def process_orders_from_json(orders_json):
    # Since orders are always provided as JSON, parse them if necessary.
    if isinstance(orders_json, str):
        orders_list = json.loads(orders_json)
    else:
        orders_list = orders_json
    orders = pd.DataFrame(orders_list)

    # Basic error checking: ensure orders DataFrame is not empty and required columns exist
    if orders.empty:
        raise ValueError("Orders JSON is empty. Please provide valid order data.")
    required_columns = ["Date", "Order_Type", "Ticker", "Shares", "Price_Per_Share"]
    missing_cols = [col for col in required_columns if col not in orders.columns]
    if missing_cols:
        raise ValueError(f"Missing required fields in orders JSON: {missing_cols}")

    # Clean and prepare orders DataFrame
    orders["Date"] = pd.to_datetime(orders["Date"])
    orders["Order_Type"] = orders["Order_Type"].str.strip().str.lower()
    orders["Ticker"] = orders["Ticker"].str.strip()
    orders.sort_values("Date", inplace=True)

    # Overall start and end dates
    start_date = orders["Date"].min()
    end_date = "2025-03-29"

    # Use the first order's ticker (assumed to be a buy) to build the portfolio index.
    first_order = orders.iloc[0]
    first_ticker = first_order["Ticker"]
    try:
        df_first = pd.read_csv(f"stockdata/{first_ticker}.csv")
    except Exception as e:
        raise ValueError(f"Error reading stock data for ticker {first_ticker}: {e}")

    df_first["Date"] = pd.to_datetime(df_first["Date"])
    mask = (df_first["Date"] >= start_date) & (df_first["Date"] <= end_date)
    filtered_close = df_first.loc[mask, ["Date", "Close"]]
    filtered_close["Daily Return"] = (
        filtered_close["Close"] / filtered_close["Close"].iloc[0]
    )

    # Create portfolio using only the dates when the market was open (from the first ticker's CSV)
    portfolio = pd.DataFrame(
        {
            "Date": filtered_close["Date"],
            first_ticker: first_order["Shares"]
            * first_order["Price_Per_Share"]
            * filtered_close["Daily Return"],
        }
    )
    portfolio.set_index("Date", inplace=True)

    # Process subsequent orders (starting from index 1)
    for idx, order in orders.iloc[1:].iterrows():
        order_date = order["Date"]
        order_type = order["Order_Type"]
        ticker = order["Ticker"]
        shares = order["Shares"]
        price = order["Price_Per_Share"]

        if order_type == "buy":
            portfolio = insert_buy_order(
                portfolio, order_date, ticker, shares, price, start_date, end_date
            )
        elif order_type == "sell":
            portfolio = insert_sell_order(
                portfolio, order_date, ticker, shares, price, start_date, end_date
            )
        else:
            print(f"Unrecognized order type: {order_type}")

    # Add the "total" column by summing across all ticker columns for each day
    portfolio["Value"] = portfolio.sum(axis=1)
    final_series = portfolio[["Value"]]
    final_series.index = final_series.index.strftime("%Y-%m-%d")
    port_val = json.loads(final_series.to_json())["Value"]
    return port_val


@app.route("/user/<oauth_sub>/portfolio", methods=["GET"])
def get_portfolio(oauth_sub):
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    session = DB.create_session()

    located_user = session.query(User).filter(User.oauth_sub == oauth_sub).first()

    if not located_user:
        return (
            jsonify({"status": 0, "error": 1, "message": "User not found"}),
            404,
        )

    #       {
    #     "Date": "2025-03-13",
    #     "Order_Type": "Buy",
    #     "Ticker": "AAPL",
    #     "Shares": 10,
    #     "Price_Per_Share": 250.0
    #   }

    user_orders = located_user.portfolio.orders

    # Sort user orders from earliest to latest
    user_orders = sorted(user_orders, key=lambda order: order.date)

    user_orders_json = [
        {
            "Date": order.date.strftime("%Y-%m-%d"),
            "Order_Type": str(order.type.value),
            "Shares": order.shares,
            "Price_Per_Share": order.price_per_share,
            "Ticker": order.ticker,
        }
        for order in user_orders
    ]

    series = process_orders_from_json(user_orders_json)

    session.close()

    return jsonify({"status": 1, "error": 0, "data": series})
