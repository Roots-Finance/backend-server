from flask import jsonify, request

from database import DB
from models import (Account, Category, Merchant, Transaction, TransactionType,
                    User)
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app

from .populate_transactions import generate_transactions

# from .user.populate_transactions import generate_transactions


@app.route("/user", methods=["POST"])
def create_user():
    """
    Route to register a new user.

    Expected Request Body:
    {
      oauth_sub: string
      plaid_key?: string
      knot_key?: string
      first_name?: string
      last_name?: string
    }
    """
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    req_json = request.get_json()

    if any(key not in req_json for key in ["oauth_sub", "first_name", "last_name"]):
        return (
            jsonify({"status": 0, "error": 1, "message": "Missing required fields"}),
            400,
        )

    session = DB.create_session()

    if session.query(User).filter(User.oauth_sub == req_json["oauth_sub"]).first():
        return (
            jsonify({"status": 0, "error": 1, "message": "User already exists"}),
            400,
        )

    new_customer = Customer(
        NessieClient,
        first_name=req_json["first_name"],
        last_name=req_json["last_name"],
        street_number="123",
        street_name="Main",
        city="New York",
        state="NY",
        zip_code="10001",
    )
    new_customer.create()

    if not new_customer.id:
        return (
            jsonify({"status": 0, "error": 1, "message": "Failed to create user"}),
            500,
        )

    new_user = User(
        oauth_sub=req_json["oauth_sub"],
        first_name=req_json["first_name"],
        last_name=req_json["last_name"],
        nessie_customer_id=new_customer.id,
    )

    if "plaid_key" in req_json:
        new_user.plaid_access_token = req_json["plaid_key"]

    if "knot_key" in req_json:
        new_user.knot_access_token = req_json["knot_key"]

    if "first_name" in req_json:
        new_user.first_name = req_json["first_name"]

    if "last_name" in req_json:
        new_user.last_name = req_json["last_name"]

    session.add(new_user)

    # Generate the transactions
    transactions = generate_transactions()

    for acc_type in [
        AccountType.CHECKING,
        AccountType.SAVINGS,
        AccountType.CREDIT_CARD,
    ]:
        new_account = new_customer.open_account(acc_type, acc_type.name)
        db_account = Account(nessie_id=new_account.id, user=new_user)
        session.add(db_account)
        for transaction in transactions[str(acc_type).lower().replace(" ", "_")]:
            # Create category in DB if does not exist
            category = (
                session.query(Category)
                .filter(Category.name == transaction["category"])
                .first()
            )
            if not category:
                category = Category(name=transaction["category"])
                session.add(category)
            # Create merchant in DB if does not exist
            merchant = (
                session.query(Merchant)
                .filter(Merchant.name == transaction["merchant"])
                .first()
            )
            if not merchant:
                merchant = Merchant(name=transaction["merchant"], category=category)
                session.add(merchant)
            db_transaction = Transaction(
                type=(
                    TransactionType.DEBIT
                    if transaction["amount"] < 0
                    else TransactionType.CREDIT
                ),
                amount=abs(transaction["amount"]),
                account=db_account,
                merchant=merchant,
                date=transaction["date"],
            )
            session.add(db_transaction)

    session.commit()
    user_json = {
        "id": new_user.id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "plaid_access_token": new_user.plaid_access_token,
        "knot_access_token": new_user.knot_access_token,
    }
    session.close()

    return jsonify(
        {"status": 1, "error": 0, "message": "User created", "data": user_json}
    )


@app.route("/user", methods=["PATCH"])
def update_user():
    """
    Expected Request Body:
    {
      oauth_sub: string
      plaid_key?: string
      knot_key?: string
      first_name?: string
      last_name?: string
    }
    """
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    req_json = request.get_json()

    if "oauth_sub" not in req_json:
        return (
            jsonify({"status": 0, "error": 1, "message": "Missing oauth_sub"}),
            400,
        )

    session = DB.create_session()

    located_user = (
        session.query(User).filter(User.oauth_sub == req_json["oauth_sub"]).first()
    )

    if not located_user:
        return (
            jsonify({"status": 0, "error": 1, "message": "User not found"}),
            404,
        )

    if "plaid_key" in req_json:
        located_user.plaid_access_token = req_json["plaid_key"]

    if "knot_key" in req_json:
        located_user.knot_access_token = req_json["knot_key"]

    if "first_name" in req_json:
        located_user.first_name = req_json["first_name"]

    if "last_name" in req_json:
        located_user.last_name = req_json["last_name"]

    session.commit()
    session.close()

    return jsonify({"status": 1, "error": 0, "message": "User updated"})


@app.route("/user/<oauth_sub>", methods=["GET"])
def get_user(oauth_sub):
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

    user_json = {
        "first_name": located_user.first_name,
        "last_name": located_user.last_name,
        "plaid_access_token": located_user.plaid_access_token,
        "knot_access_token": located_user.knot_access_token,
    }

    return jsonify({"status": 1, "error": 0, "data": user_json})
