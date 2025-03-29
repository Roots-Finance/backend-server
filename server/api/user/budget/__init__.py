from flask import jsonify, request

from database import DB
from models import Account, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/user/<oauth_sub>/budget", methods=["GET"])
def get_budget(oauth_sub):
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

    session.close()

    return jsonify({"status": 1, "error": 0, "data": located_user.budget_configuration})


@app.route("/user/<oauth_sub>/budget", methods=["PATCH"])
def update_budget(oauth_sub):
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

    located_user.budget_configuration = req_json

    session.commit()

    session.close()

    return jsonify({"status": 1, "error": 0, "data": req_json})
