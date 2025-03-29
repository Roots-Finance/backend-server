from flask import jsonify, request

from database import DB
from models import User
from nessie import Customer, NessieClient
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
