import pandas as pd
import json
from collections import defaultdict
from tabulate import tabulate

# Mapping: CSV files (in subfolder) to the corresponding transaction category
csv_to_category = {
    'cleaned_tables/drugstore.csv': 'Health',
    'cleaned_tables/household_bills.csv': 'Bills and Utilities',
    'cleaned_tables/restaurant.csv': 'Food and Dining',
    'cleaned_tables/supermarkets.csv': 'Food and Dining',
    'cleaned_tables/gas.csv': 'Transportation',
    'cleaned_tables/travel.csv': 'Transportation',
    # 'cleaned_tables/wholesale_clubs.csv': 'Shopping'
}

# Group CSV files by normalized category (lowercase)
category_to_csvs = defaultdict(list)
for csv_file, cat in csv_to_category.items():
    norm_cat = cat.strip().lower()
    category_to_csvs[norm_cat].append(csv_file)

# Load transactions from JSON
with open('transactions.json', 'r') as f:
    transactions = json.load(f)

# Normalize the transaction categories
for t in transactions:
    t['category'] = t['category'].strip().lower()

# Compute total spending per category (using the normalized category)
category_total_spending = {}
for cat in category_to_csvs.keys():
    spending = sum(t['amount'] for t in transactions if t['category'] == cat)
    category_total_spending[cat] = spending

# For each category, accumulate the best (highest) cashback for each card across all its CSV files.
category_results = {}  # mapping: normalized category -> dict with key=(Bank Name, Card Name), value=best cashback rate
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
            bank = row['Bank Name']
            card = row['Card Name']
            try:
                cashback = float(row['Cashback'])
            except Exception as e:
                print(f"Error converting cashback for {bank} - {card}: {e}")
                continue
            key = (bank, card)
            # If the card already has an offer, keep the highest cashback rate.
            offers[key] = max(offers.get(key, 0), cashback)
    category_results[cat] = offers

# Build a list for each category: (bank, card, cashback, savings)
category_savings_list = {}
for cat, offers in category_results.items():
    spending = category_total_spending.get(cat, 0)
    results = []
    for (bank, card), cashback in offers.items():
        savings = spending * cashback
        results.append((bank, card, cashback, savings))
    # Sort descending by savings
    results.sort(key=lambda x: x[3], reverse=True)
    category_savings_list[cat] = results

# Aggregate total savings across all categories per card
total_savings = defaultdict(float)
for cat, results in category_savings_list.items():
    for bank, card, cashback, savings in results:
        total_savings[(bank, card)] += savings

total_savings_sorted = sorted(total_savings.items(), key=lambda x: x[1], reverse=True)

# Pretty print the results by category using tabulate

print("Best Rewards by Category:\n")
for cat, results in category_savings_list.items():
    # Use a friendlier display name; for example, show "Transport" instead of "Transportation"
    display_cat = "Transport" if cat == "transportation" else cat.title()
    table_data = []
    for bank, card, cashback, savings in results:
        table_data.append([bank, card, f"{cashback:.4f}", f"${savings:.2f}"])
    print(f'Best Rewards for "{display_cat}":')
    print(tabulate(table_data, headers=["Bank Name", "Card Name", "Cashback", "Total Savings"], tablefmt="pretty"))
    print("\n")

# Pretty print the overall total savings
total_table = []
for (bank, card), savings in total_savings_sorted:
    total_table.append([bank, card, f"${savings:.2f}"])
print("Best Rewards for Total Across Categories:")
print(tabulate(total_table, headers=["Bank Name", "Card Name", "Total Savings"], tablefmt="pretty"))
