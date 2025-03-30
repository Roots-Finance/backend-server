import json
import os
from collections import defaultdict

import pandas as pd
from flask import jsonify, request

from database import DB
from models import Account, Order, OrderType, Portfolio, Transaction, User
from nessie import Account as NessieAccount
from nessie import AccountType, Customer, NessieClient
from server.app import api_router as app


def calculate_rewards(transactions):
    # Mapping: CSV files (in subfolder) to the corresponding transaction category
    csv_to_category = {
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/drugstore.csv"
        ): "Health",
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/household_bills.csv"
        ): "Bills and Utilities",
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/restaurant.csv"
        ): "Food and Dining",
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/supermarket.csv"
        ): "Food and Dining",
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/gas.csv"
        ): "Transportation",
        os.path.join(
            os.getcwd(), "card_rewards/cleaned_tables/travel.csv"
        ): "Transportation",
        # 'cleaned_tables/wholesale_clubs.csv': 'Shopping'
    }

    # Group CSV files by normalized category (lowercase)
    category_to_csvs = defaultdict(list)
    for csv_file, cat in csv_to_category.items():
        norm_cat = cat.strip().lower()
        category_to_csvs[norm_cat].append(csv_file)

    # Normalize the transaction categories
    for t in transactions:
        t["category"] = t["category"].strip().lower()

    # Compute total spending per category (using the normalized category)
    category_total_spending = {}
    for cat in category_to_csvs.keys():
        spending = sum(t["amount"] for t in transactions if t["category"] == cat)
        category_total_spending[cat] = spending

    # For each category, accumulate the best (highest) cashback for each card across all its CSV files.
    # Now we also store the URL and image_url.
    category_results = (
        {}
    )  # mapping: normalized category -> dict with key=(Bank Name, Card Name), value=dict{cashback, url, image_url}
    for cat, csv_files in category_to_csvs.items():
        offers = {}
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")
                continue
            # For each row in the rewards CSV
            for _, row in df.iterrows():
                bank = row["Bank Name"]
                card = row["Card Name"]
                try:
                    cashback = float(row["Cashback"])
                except Exception as e:
                    print(f"Error converting cashback for {bank} - {card}: {e}")
                    continue
                url = row.get("url", "")
                image_url = row.get("image_url", "")
                key = (bank, card)
                # If the card already has an offer, keep the one with the highest cashback rate.
                if key in offers:
                    if cashback > offers[key]["cashback"]:
                        offers[key] = {
                            "cashback": cashback,
                            "url": url,
                            "image_url": image_url,
                        }
                else:
                    offers[key] = {
                        "cashback": cashback,
                        "url": url,
                        "image_url": image_url,
                    }
        category_results[cat] = offers

    # Build a list for each category: (bank, card, cashback, savings, url, image_url)
    category_savings_list = {}
    for cat, offers in category_results.items():
        spending = category_total_spending.get(cat, 0)
        results = []
        for (bank, card), data in offers.items():
            cashback = data["cashback"]
            savings = spending * cashback
            results.append(
                (bank, card, cashback, savings, data["url"], data["image_url"])
            )
        # Sort descending by savings
        results.sort(key=lambda x: x[3], reverse=True)
        category_savings_list[cat] = results

    # Aggregate total savings across all categories per card.
    # Also accumulate the card details (url and image_url) for the overall table.
    total_savings = defaultdict(float)
    card_details = {}
    for cat, results in category_savings_list.items():
        for bank, card, cashback, savings, url, image_url in results:
            total_savings[(bank, card)] += savings
            # Save details if not already stored (or update if needed)
            if (bank, card) not in card_details:
                card_details[(bank, card)] = {"url": url, "image_url": image_url}

    total_savings_sorted = sorted(
        total_savings.items(), key=lambda x: x[1], reverse=True
    )

    for cat, results in category_savings_list.items():
        # Use a friendlier display name; for example, "Transport" instead of "Transportation"
        display_cat = "Transport" if cat == "transportation" else cat.title()
        table_data = []
        for bank, card, cashback, savings, url, image_url in results:
            table_data.append([bank, card, f"{cashback:.4f}", f"${savings:.2f}"])

    total_table = []
    for (bank, card), savings in total_savings_sorted:
        details = card_details.get((bank, card), {})
        url = details.get("url", "")
        image_url = details.get("image_url", "")
        total_table.append([bank, card, f"${savings:.2f}", url, image_url])

    json_return = {}
    for i in range(5):
        json_return[i + 1] = {
            "bank": total_table[i][0],
            "card": total_table[i][1],
            "savings": total_table[i][2],
            "url": total_table[i][3],
            "image_url": total_table[i][4],
        }

    return json_return


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
    results = calculate_rewards(transactions_json)

    return jsonify({"status": 1, "error": 0, "data": results})
