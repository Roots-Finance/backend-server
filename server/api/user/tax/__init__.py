import base64
import json
import os

from flask import jsonify, request
from google import genai
from google.genai import types

from database import DB
from models import Account, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


def generate(prompt: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    data_str = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        data_str += chunk.text

    # the string starts with ```json and ends with ```
    # get rid of it

    data_str = data_str.replace("```json", "").replace("```", "")
    return json.loads(data_str)


@app.route("/user/<oauth_sub>/taxes", methods=["GET"])
def tax_report(oauth_sub):
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

    prompt = f"""
    Here is a users spending for the past 24 months.

    You are an expert accountant and premier US tax expert.
    With the above data, you will generate a tax report for the user.
    Return the report as a JSON object.
    Try to include as many deductions as possible, and try to estimate the amount, I never want it to be 0. In any reason, you are speaking in first person, directly to the user.

    Match the following format

    {{
        "TaxYearsCovered": [],
        "IncomeSummary": {{
            "<year>": {{
                "TaxableIncome": ,
                "TaxLiability": ,
                "PotentialDeductions": [
                    {{
                        "Name": "",
                        "Reason": ""
                        "Amount": 
                    }}
                ],
                "TotalPotentialDeductions": 
        }}
    }}

    {json.dumps(transactions_json)}
    """

    response = generate(prompt)

    return jsonify({"status": 1, "error": 0, "data": response}), 200
