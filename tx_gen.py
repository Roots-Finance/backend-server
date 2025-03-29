import json
import random
import uuid
from datetime import datetime, timedelta

# Define transaction categories and corresponding merchants
categories = {
    "Food and Dining": [
        {
            "name": "Grocery Shopping",
            "merchants": [
                "Kroger",
                "Whole Foods",
                "Trader Joe's",
                "Safeway",
                "Costco",
                "Walmart",
                "Target",
                "Aldi",
            ],
        },
        {
            "name": "Restaurants",
            "merchants": [
                "Chipotle",
                "Panera Bread",
                "Olive Garden",
                "Chili's",
                "Applebee's",
                "Cheesecake Factory",
                "Subway",
                "McDonald's",
                "Starbucks",
            ],
        },
        {
            "name": "Food Delivery",
            "merchants": ["DoorDash", "Uber Eats", "Grubhub", "Instacart"],
        },
    ],
    "Transportation": [
        {"name": "Gas", "merchants": ["Shell", "Exxon", "BP", "Chevron", "Circle K"]},
        {"name": "Ride Sharing", "merchants": ["Uber", "Lyft"]},
        {
            "name": "Public Transit",
            "merchants": ["Transit Authority", "Metro", "Train Station"],
        },
    ],
    "Shopping": [
        {
            "name": "Clothing",
            "merchants": [
                "Amazon",
                "Target",
                "Walmart",
                "Old Navy",
                "TJ Maxx",
                "Macy's",
                "Kohl's",
                "Gap",
            ],
        },
        {
            "name": "Electronics",
            "merchants": ["Best Buy", "Apple Store", "Amazon", "Newegg", "GameStop"],
        },
        {
            "name": "Home Goods",
            "merchants": [
                "Bed Bath & Beyond",
                "Home Depot",
                "Lowe's",
                "IKEA",
                "Wayfair",
                "Target",
            ],
        },
    ],
    "Entertainment": [
        {
            "name": "Streaming Services",
            "merchants": [
                "Netflix",
                "Hulu",
                "Disney+",
                "HBO Max",
                "Spotify",
                "Amazon Prime",
            ],
        },
        {"name": "Movies", "merchants": ["AMC Theaters", "Regal Cinemas", "Cinemark"]},
        {
            "name": "Activities",
            "merchants": ["Bowling Alley", "Mini Golf", "Zoo", "Museum", "Arcade"],
        },
    ],
    "Health": [
        {"name": "Pharmacy", "merchants": ["CVS", "Walgreens", "Rite Aid"]},
        {
            "name": "Doctor's Office",
            "merchants": ["Family Doctor", "Urgent Care", "Medical Center"],
        },
        {
            "name": "Fitness",
            "merchants": [
                "Planet Fitness",
                "LA Fitness",
                "24 Hour Fitness",
                "Yoga Studio",
                "Peloton",
            ],
        },
    ],
    "Bills and Utilities": [
        {"name": "Electricity", "merchants": ["Electric Company", "Energy Provider"]},
        {"name": "Water", "merchants": ["Water Utility"]},
        {"name": "Internet", "merchants": ["Comcast", "AT&T", "Verizon", "Spectrum"]},
        {"name": "Phone", "merchants": ["Verizon", "AT&T", "T-Mobile"]},
    ],
    "Home": [
        {
            "name": "Rent/Mortgage",
            "merchants": ["Property Management", "Mortgage Lender", "Bank"],
        },
        {
            "name": "Insurance",
            "merchants": ["State Farm", "Progressive", "Geico", "Liberty Mutual"],
        },
    ],
    "Personal Care": [
        {"name": "Haircut", "merchants": ["Great Clips", "Supercuts", "Local Salon"]},
        {"name": "Spa/Massage", "merchants": ["Massage Envy", "Local Spa"]},
    ],
    "Education": [
        {"name": "Tuition", "merchants": ["University", "Community College"]},
        {
            "name": "Books and Supplies",
            "merchants": ["Amazon", "University Bookstore", "Chegg"],
        },
    ],
}

# Common transaction amounts by category
amount_ranges = {
    "Food and Dining": {
        "Grocery Shopping": (50, 250),
        "Restaurants": (15, 85),
        "Food Delivery": (20, 60),
    },
    "Transportation": {
        "Gas": (35, 65),
        "Ride Sharing": (10, 40),
        "Public Transit": (2, 25),
    },
    "Shopping": {
        "Clothing": (25, 150),
        "Electronics": (50, 1000),
        "Home Goods": (30, 300),
    },
    "Entertainment": {
        "Streaming Services": (8, 20),
        "Movies": (15, 50),
        "Activities": (20, 100),
    },
    "Health": {
        "Pharmacy": (10, 100),
        "Doctor's Office": (20, 250),
        "Fitness": (15, 120),
    },
    "Bills and Utilities": {
        "Electricity": (80, 300),
        "Water": (40, 120),
        "Internet": (60, 150),
        "Phone": (40, 180),
    },
    "Home": {"Rent/Mortgage": (1200, 2500), "Insurance": (80, 300)},
    "Personal Care": {"Haircut": (20, 80), "Spa/Massage": (60, 200)},
    "Education": {"Tuition": (500, 3000), "Books and Supplies": (50, 300)},
}


# Generate a realistic looking transaction id
def generate_transaction_id():
    return f"tx_{uuid.uuid4().hex[:16]}"


# Generate a realistic account id
def generate_account_id():
    return f"acct_{uuid.uuid4().hex[:12]}"


# Generate transaction data
def generate_transactions(num_transactions=100):
    transactions = []
    account_ids = {
        "credit_card": "CREDIT_CARD",
        "checking_account": "CHECKING",
        "savings_account": "SAVINGS",
    }

    # Start date: 3 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    for _ in range(num_transactions):
        # Choose a random date between start_date and end_date
        days_between = (end_date - start_date).days
        random_day = random.randint(0, days_between)
        transaction_date = (start_date + timedelta(days=random_day)).strftime(
            "%Y-%m-%d"
        )

        # Randomly choose an account type
        account_type = random.choices(
            ["credit_card", "checking_account", "savings_account"],
            weights=[0.4, 0.2, 0.4],  # More weight on credit and checking
            k=1,
        )[0]

        # Determine transaction type based on account type
        if account_type == "savings_account":
            # Only deposits and transfers
            transaction_name = "Deposit" if random.random() < 0.5 else "Transfer"
            amount = round(
                random.uniform(50, 1000), 2
            )  # Example amount range for deposits
            merchant = "Bank"  # Generic merchant for deposits/transfers
        elif account_type == "checking_account":
            # Can spend and pay credit card bills
            category = random.choice(list(categories.keys()))
            transaction_type = random.choice(categories[category])
            transaction_name = transaction_type["name"]
            merchant = random.choice(transaction_type["merchants"])
            amount_min, amount_max = amount_ranges[category].get(
                transaction_name, (10, 100)
            )
            amount = round(random.uniform(amount_min, amount_max), 2)
            # Add a rule to pay credit card bills
            if transaction_name == "Rent/Mortgage":
                amount = round(
                    random.uniform(1200, 2500), 2
                )  # Example for rent/mortgage
                merchant = "Property Management"
        else:  # credit_card
            category = random.choice(list(categories.keys()))
            transaction_type = random.choice(categories[category])
            transaction_name = transaction_type["name"]
            merchant = random.choice(transaction_type["merchants"])
            amount_min, amount_max = amount_ranges[category].get(
                transaction_name, (10, 100)
            )
            amount = round(random.uniform(amount_min, amount_max), 2)

        # Create transaction object
        # Create transaction object
        transaction = {
            "amount": amount,
            "account_id": account_ids[account_type],
            "transaction_id": generate_transaction_id(),
            "date": transaction_date,
            "merchant_name": merchant,
            "category": transaction_name,
            "pending": False,
        }

        transactions.append(transaction)

    # Sort transactions by date (newest first)
    transactions.sort(key=lambda x: x["date"], reverse=True)

    return transactions


# Generate 100 transactions
transactions = generate_transactions(100)


# Print as JSON
# print(json.dumps(transactions, indent=2))


cc_spend = 0
checking_spend = 0
savings_spend = 0


for transaction in transactions:
    if transaction["account_id"] == "CREDIT_CARD":
        cc_spend += transaction["amount"]
    elif transaction["account_id"] == "CHECKING":
        checking_spend += transaction["amount"]
    elif transaction["account_id"] == "SAVINGS":
        print(json.dumps(transaction, indent=2))
        savings_spend += transaction["amount"]


print(f"Total spend on credit card: ${cc_spend}")
print(f"Total spend on checking account: ${checking_spend}")
print(f"Total spend on savings account: ${savings_spend}")
