from flask import jsonify, request

from database import DB
from models import Account, Transaction, TransactionType, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/account/<id>/nessie-transactions", methods=["GET"])
def get_transactions(id):
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    session = DB.create_session()

    located_account = session.query(Account).filter(Account.id == id).first()

    if not located_account:
        return (
            jsonify({"status": 0, "error": 1, "message": "Account not found"}),
            404,
        )

    transactions = session.query(Transaction).filter(Transaction.account_id == id).all()

    transaction_json = []

    for transaction in transactions:
        transaction_json.append(
            {
                "id": transaction.id,
                "type": (
                    "DEBIT" if transaction.type == TransactionType.DEBIT else "CREDIT"
                ),
                "amount": transaction.amount,
                "date": transaction.date,
                "merchant": transaction.merchant.name,
                "category": transaction.merchant.category.name,
            }
        )

    session.close()
    #     nessie_acc = NessieAccount(NessieClient)
    #     nessie_acc.get_account(located_account.nessie_id)
    #
    #     purchases = nessie_acc.get_purchases()
    #
    #     transaction_json = []
    #
    #     for purchase in purchases:
    #         transaction_json.append(
    #             {
    #                 "id": purchase.id,
    #                 "type": str(purchase.type),
    #                 "merchant_id": purchase.merchant_id,
    #                 "payer_id": purchase.payer_id,
    #                 "amount": purchase.amount,
    #                 "purchase_date": purchase.purchase_date,
    #                 "status": purchase.status,
    #                 "medium": purchase.medium,
    #                 "description": purchase.description,
    #             }
    #         )

    return jsonify({"status": 1, "error": 0, "data": transaction_json})
