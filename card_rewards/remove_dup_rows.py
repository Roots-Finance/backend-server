import os
import pandas as pd

files = [
    'cleaned_tables/drugstore.csv',
    'cleaned_tables/household_bills.csv',
    'cleaned_tables/restaurant.csv',
    'cleaned_tables/supermarket.csv',
    'cleaned_tables/gas.csv',
    'cleaned_tables/travel.csv',
    'cleaned_tables/wholesale_clubs.csv'
]

# i made this but don't wanna commit two table dirs so I just commiting "cleaned_tables"
os.makedirs("final_tables", exist_ok=True)

for file in files:
    df = pd.read_csv(file)
    # removing duplicate rows, think of bank name + card name as the primary key    
    df_unique = df.drop_duplicates(subset=['Bank Name', 'Card Name'], keep='first')
    base_filename = os.path.basename(file)
    output_file = os.path.join("final_tables", base_filename)
    df_unique.to_csv(output_file, index=False)
    
    print(f"Processed {file} -> {output_file}")
