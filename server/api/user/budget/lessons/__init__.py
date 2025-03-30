import json
import os

from flask import jsonify, request
from google import genai
from google.genai import types

from database import DB
from models import Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


@app.route("/user/<oauth_sub>/lessons", methods=["GET"])
def lessons(oauth_sub):
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
    
    # Generate personalized lessons content using Gemini
    lessons_data = generate_lessons_content(transactions_json)
    
    return jsonify(
        {
            "status": 1,
            "error": 0,
            "data": lessons_data,
        }
    )


def generate(prompt: str):
    """Generate content using Google's Gemini API"""
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


def generate_lessons_content(transactions_json):
    """Generate personalized lessons content based on transaction data"""
    
    # Analyze transactions to find spending patterns
    categories = {}
    for tx in transactions_json:
        if tx.get("category") and not tx.get("type") == "CREDIT":
            cat = tx.get("category")
            if cat in categories:
                categories[cat] += tx.get("amount", 0)
            else:
                categories[cat] = tx.get("amount", 0)
    
    # Find top spending categories
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    top_categories = [cat[0] for cat in sorted_categories[:3]]
    
    # to keep things reasonable, limit to X transactions
    # but spread them evenly across the timeframe of the transactions
    end_idx = len(transactions_json)
    indexer = end_idx / 50
    
    seen = set()
    storage = []
    for i in range(50):
        # round down the index if a float
        approx_idx = int(i * indexer)
        
        if approx_idx >= end_idx:
            break
        if approx_idx in seen:
            continue
        storage.append(transactions_json[approx_idx])
        seen.add(approx_idx)
        
        
    
    
    prompt = f"""
    You are a personal finance advisor. Based on the user's transaction data, create personalized lessons and resources. 
    
    The user's top spending categories are: {", ".join(top_categories)}.
    
    Return only a JSON object that follows this structure exactly:
    {{
      "title": "Budgeting Fundamentals",
      "description": "Learn how to create and maintain a personal budget that helps you achieve your financial goals.",
      "lessons": [
        {{
          "id": "string-id",
          "title": "Lesson Title",
          "description": "Brief description of the lesson",
          "duration": "X min",
          "content": [
            {{
              "title": "Section Title",
              "content": "Section content",
              "completed": false
            }}
          ]
        }}
      ],
      "resources": [
        {{
          "id": "resource-id",
          "title": "Resource Title",
          "type": "Article/Video/Tool/Spreadsheet/Calculator",
          "url": "https://example.com",
          "description": "Brief description of the resource"
        }}
      ]
    }}
    
    Rules:
    1. Create 3-4 lessons that are personalized to the user's spending patterns
    2. At least one lesson should focus specifically on the user's top spending category
    3. Each lesson should have 3-5 content sections
    4. Each section in a lesson should flow from the next. Introduce concepts progressively
    5. Every section should mention specific events or transactions from the user's data to emphasize relevance
    6. Include 3-5 relevant resources
    7. All URLs must be real, working URLs to legitimate financial education websites.
    8. Make the content actionable and specific
    9. Set all "completed" values to false
    10. Include a mix of resource types (articles, tools, calculators, etc.)
    11. Use descriptive IDs that relate to the content
    
    Transaction data:
    {json.dumps(storage)}  # Limit to 50 transactions to keep prompt size reasonable
    """
    
    try:
        return generate(prompt)
    except Exception as e:
        print(f"Error generating lessons content: {e}")
        # Fallback to basic content if generation fails
        return {
            "title": "Budgeting Fundamentals",
            "description": "Learn how to create and maintain a personal budget that helps you achieve your financial goals.",
            "lessons": [
                {
                    "id": "budget-basics",
                    "title": "Budget Basics",
                    "description": "Learn the fundamentals of creating and maintaining a personal budget.",
                    "duration": "15 min",
                    "content": [
                        {
                            "title": "What is a Budget?",
                            "content": "A budget is a financial plan that helps you track your income and expenses over a period of time.",
                            "completed": False
                        },
                        {
                            "title": "The 50/30/20 Rule",
                            "content": "The 50/30/20 rule is a simple budgeting framework that allocates 50% of your income to needs, 30% to wants, and 20% to savings and debt repayment.",
                            "completed": False
                        }
                    ]
                }
            ],
            "resources": [
                {
                    "id": "budget-template",
                    "title": "Simple Budget Template",
                    "type": "Spreadsheet",
                    "url": "https://www.consumerfinance.gov/consumer-tools/budget-template/",
                    "description": "A free budget spreadsheet from the Consumer Financial Protection Bureau."
                }
            ]
        }