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

    return jsonify({"status": 1, "error": 0, "data": accounts_json})


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


@app.route("/user/<oauth_sub>/ai-budget", methods=["GET"])
def ai_budget(oauth_sub):
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
    Here is a users spending for the past 3 months.

    For each category, provide the percentage of spending that should be KEPT in order to try and save money.
    Provide the following format and only the following format, no explanation.
    Some of these categories probably shouldn't be cut at all, and thats fine.

    {{
    "category_name": percentage,
    }}

    Finally, the final key in the json object should be "reasoning" I'd like you to explain where you made cuts, why, why didn't you make cuts, etc. Reasoning should be in first person, talking directly to the user. Highlight specific purchases or observable trends in your reasoning. Additionally, comment exclusively on discretionary purchases. Respond in a bullet point format. Importantly, if a category is only responsible for credits, do not comment on it at all. The bullet points should be their own string in an array, no hyphen or anything denoting the fact that it is a bullet point required.

    {json.dumps(transactions_json)}
    """

    response = generate(prompt)

    return jsonify({"status": 1, "error": 0, "data": response})
