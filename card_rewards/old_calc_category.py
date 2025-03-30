import pandas as pd
import json

#! DEPRECATED

# for individual tables (changed this manuyally and ran it over each one)
transport_rewards = pd.read_csv('cleaned_tables/travel.csv')

with open('transactions.json', 'r') as f:
    transactions = json.load(f)

transport_transactions = [t for t in transactions if t['category'].lower() == 'transportation']

# Compute the total spending on each category
total_spending = sum(t['amount'] for t in transport_transactions)

# Calculate savings for each card
transport_rewards['Total Savings'] = transport_rewards['Cashback'] * total_spending

# only displaying relevant cols
print(transport_rewards[['Bank Name', 'Card Name', 'Cashback', 'Total Savings']])
