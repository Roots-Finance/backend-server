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


@app.route("/user/<oauth_sub>/portfolio/preferences", methods=["POST"])
def set_portfolio(oauth_sub):
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    req_json = request.get_json()

    required_fields = [
        "is_experienced_investor",
        "preferred_sectors",
        "sector_preference_rankings",
        "market_cap_preference",
        "growth_vs_value",
        "cyclical_vs_defensive",
        "valuation_metrics_preference",
        "dividend_preference",
        "tech_sector_interest",
        "healthcare_sector_interest",
        "financial_sector_interest",
        "consumer_goods_interest",
        "industrials_interest",
        "emerging_markets_interest",
        "ESG_preference",
        "small_cap_interest",
        "blue_chip_interest",
        "tech_subsectors_interest",
        "healthcare_subsectors_interest",
        "investment_time_horizon",
    ]

    if any(key not in req_json for key in required_fields):
        missing_fields = ", ".join(
            [key for key in required_fields if key not in req_json]
        )
        return (
            jsonify(
                {
                    "status": 0,
                    "error": 1,
                    "message": f"Missing required fields: {missing_fields}",
                }
            ),
            400,
        )

    session = DB.create_session()

    located_user = session.query(User).filter(User.oauth_sub == oauth_sub).first()

    if not located_user:
        return (
            jsonify({"status": 0, "error": 1, "message": "User not found"}),
            404,
        )

    located_user.is_experienced_investor = req_json["is_experienced_investor"]
    located_user.preferred_sectors = ", ".join(req_json["preferred_sectors"])
    located_user.sector_preference_rankings = ", ".join(
        req_json["sector_preference_rankings"]
    )
    located_user.market_cap_preference = req_json["market_cap_preference"]
    located_user.growth_vs_value = req_json["growth_vs_value"]
    located_user.cyclical_vs_defensive = req_json["cyclical_vs_defensive"]
    located_user.valuation_metrics_preference = req_json["valuation_metrics_preference"]
    located_user.dividend_preference = req_json["dividend_preference"]
    located_user.tech_sector_interest = req_json["tech_sector_interest"]
    located_user.healthcare_sector_interest = req_json["healthcare_sector_interest"]
    located_user.financial_sector_interest = req_json["financial_sector_interest"]
    located_user.consumer_goods_sector_interest = req_json["consumer_goods_interest"]
    located_user.industrials_sector_interest = req_json["industrials_interest"]
    located_user.energy_sector_interest = req_json["energy_sector_interest"]
    located_user.emerging_markets_interest = req_json["emerging_markets_interest"]
    located_user.esg_preference = req_json["ESG_preference"]
    located_user.small_cap_interest = req_json["small_cap_interest"]
    located_user.blue_chip_interest = req_json["blue_chip_interest"]
    located_user.tech_subsectors_interest = ", ".join(
        req_json["tech_subsectors_interest"]
    )
    located_user.healthcare_subsectors_interest = ", ".join(
        req_json["healthcare_subsectors_interest"]
    )
    located_user.investment_time_horizon = req_json["investment_time_horizon"]

    #     date": "string (ISO format date)",
    #       "symbol": "string (stock ticker symbol)",
    #       "transaction_type": "string (buy, sell)",
    #       "quantity": "string (number of shares)",
    #       "price": "string (price per share)",
    #       "total": "string (total transaction amount)"

    if not located_user.portfolio:
        portfolio = Portfolio(user=located_user)
        session.add(portfolio)
        located_user.portfolio = portfolio

    if req_json["is_experienced_investor"] is True:
        located_user.has_trade_history = req_json["has_trade_history"]

    if (
        req_json["is_experienced_investor"] is True
        and req_json["has_trade_history"] is True
    ):
        for order in req_json["trade_history_data"]:
            new_order = Order(
                date=parse(order["date"]),
                type=OrderType(order["transaction_type"].upper()),
                shares=float(order["quantity"]),
                price_per_share=float(order["price"]),
                ticker=order["symbol"],
                portfolio=located_user.portfolio,
            )

            session.add(new_order)

    session.commit()

    session.close()

    return jsonify({"status": 1, "error": 0, "message": "Portfolio updated"})


@app.route("/user/<oauth_sub>/portfolio/preferences", methods=["GET"])
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

    if not located_user.portfolio:
        return (
            jsonify({"status": 0, "error": 1, "message": "Portfolio not found"}),
            404,
        )

    if located_user.esg_preference is not None:
        session.close()
        return (jsonify({"status": 1, "error": 0, "message": "Preferences set"})), 200
    session.close()
    return (jsonify({"status": 0, "error": 1, "message": "Preferences not set"})), 404

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
