from flask import jsonify, request

from database import DB
from models import Account, Order, OrderType, Portfolio, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/user/<oauth_sub>/cards", methods=["GET"])
def recommend_cards(oauth_sub):
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

    transactions_json = []

    for account in located_user.accounts:
        transactions = (
            session.query(Transaction)
            .filter(Transaction.account_id == account.id)
            .all()
        )
        for transaction in transactions:
            transactions_json.append(
                {
                    "amount": transaction.amount,
                    "type": str(transaction.type),
                    "date": str(transaction.date),
                    "merchant": transaction.merchant.name,
                    "category": transaction.merchant.category.name,
                }
            )

    session.close()

    # Call Credit Card Recommendation Function

    return jsonify({"status": 1, "error": 0, "message": "Not implemented yet"})
