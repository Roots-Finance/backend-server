import base64
import json
import os

from dateutil.parser import parse
from flask import jsonify, request
from google import genai
from google.genai import types

from database import DB
from models import Account, Order, OrderType, Portfolio, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/user/<oauth_sub>/portfolio", methods=["POST"])
def set_portfolio(oauth_sub):
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    req_json = request.get_json()

    session = DB.create_session()

    located_user = session.query(User).filter(User.oauth_sub == oauth_sub).first()

    if not located_user:
        return (
            jsonify({"status": 0, "error": 1, "message": "User not found"}),
            404,
        )

    for order in req_json["orders"]:
        new_order = Order(
            date=order["date"],
            type=order["type"],
            shares=order["shares"],
            price_per_share=order["price_per_share"],
            ticker=order["ticker"],
            portfolio=located_user.portfolio,
        )

        session.add(new_order)

    session.commit()

    session.close()

    return jsonify({"status": 1, "error": 0, "message": "Portfolio updated"})


@app.route("/user/<oauth_sub>/portfolio", methods=["GET"])
def portfolio_timeseries(oauth_sub):
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

    user_orders = located_user.portfolio.orders

    # Sort user orders from earliest to latest
    user_orders = sorted(user_orders, key=lambda order: order.date)

    user_orders_json = [
        {
            "date": order.date.strftime("%Y-%m-%d"),
            "type": str(order.type.value),
            "shares": order.shares,
            "price_per_share": order.price_per_share,
        }
        for order in user_orders
    ]

    session.close()

    return jsonify({"status": 1, "error": 0, "data": user_orders_json})
