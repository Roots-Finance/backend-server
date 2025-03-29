from flask import jsonify, request

from database import DB
from models import Account, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app

from .populate_transactions import generate_transactions


@app.route("/user/<oauth_sub>/accounts", methods=["GET"])
def get_user_accounts(oauth_sub):
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

    accounts_json = []

    transactions = generate_transactions(100)

    for account in located_user.accounts:
        nessie_acc = NessieAccount(NessieClient)
        nessie_acc.get_account(account.nessie_id)
        accounts_json.append(
            {
                "id": account.id,
                "type": str(nessie_acc.type),
                "nickname": nessie_acc.nickname,
                "rewards": nessie_acc.rewards,
                "balance": nessie_acc.balance,
            }
        )

    session.close()

    return jsonify({"status": 1, "error": 0, "accounts": accounts_json})
