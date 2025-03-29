from flask import jsonify, request

from database import DB
from models import Account, User
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/user", methods=["POST"])
def create_user():
    """
    Route to register a new user.

    Expected Request Body:
    {
        "oauth_sub": ""
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

    session.add(new_user)

    for acc_type in [
        AccountType.CHECKING,
        AccountType.SAVINGS,
        AccountType.CREDIT_CARD,
    ]:
        new_account = new_customer.open_account(acc_type, acc_type.name)
        db_account = Account(nessie_id=new_account.id, user=new_user)
        session.add(db_account)

    session.commit()
    session.close()

    return jsonify(
        {
            "status": 1,
            "error": 0,
            "message": "User created",
            "user": {
                "nessie_customer_id": new_customer.id,
            },
        }
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
