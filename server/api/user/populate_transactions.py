import random
from datetime import datetime, timedelta

# Define the categories and merchants as provided
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


# Function to generate a random date within the last three months
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def generate_transactions():
    transactions = {"checking": [], "savings": [], "credit_card": []}

    # Define the time frame for 24 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    total_income = 0
    total_checking_spending = 0
    total_credit_card_spending = 0

    for _ in range(48):

        amount = random.randint(1000, 3000)  # Random income amount
        total_income += amount
        transactions["savings"].append(
            {
                "date": random_date(start_date, end_date).date(),
                "category": "Income Deposit",
                "merchant": "Salary",
                "amount": amount,
            }
        )

    # Generate transactions for checking account
    for _ in range(80):  # Random number of spending transactions
        category = random.choice(list(categories.keys()))
        merchant = random.choice(random.choice(categories[category])["merchants"])
        amount = random.randint(10, 500)  # Random spending amount
        total_checking_spending += amount
        transactions["checking"].append(
            {
                "date": random_date(start_date, end_date).date(),
                "category": category,
                "merchant": merchant,
                "amount": -amount,  # Negative for spending
            }
        )

    # Generate deposits for checking account
    for _ in range(24):  # Random number of deposit transactions
        amount = random.randint(100, 1000)  # Random deposit amount
        transactions["checking"].append(
            {
                "date": random_date(start_date, end_date).date(),
                "category": "Deposit",
                "merchant": "Bank",
                "amount": amount,
            }
        )

    # Generate transactions for credit card
    for _ in range(120):  # Random number of spending transactions
        category = random.choice(list(categories.keys()))
        merchant = random.choice(random.choice(categories[category])["merchants"])
        amount = random.randint(20, 800)  # Random spending amount
        total_credit_card_spending += amount
        transactions["credit_card"].append(
            {
                "date": random_date(start_date, end_date).date(),
                "category": category,
                "merchant": merchant,
                "amount": -amount,  # Negative for spending
            }
        )

    # Ensure total income is between $500 and $1500 greater than total spending
    total_spending = total_checking_spending + total_credit_card_spending
    if total_income <= total_spending + 500:
        additional_income = (
            (total_spending + 500) - total_income + random.randint(0, 1000)
        )
        total_income += additional_income

        # Add the additional income to the savings account
        transactions["savings"].append(
            {
                "date": random_date(start_date, end_date).date(),
                "category": "Income Adjustment",
                "merchant": "Additional Income",
                "amount": additional_income,
            }
        )

    return transactions
