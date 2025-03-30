import os
import pandas as pd

# Define the input file name (I ran this individually over each csv))
input_file = "wholesale_clubs.csv"

output_dir = "cleaned_tables"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_file)

# each of the tables had diff cashback cols so i renamed them for each run
df.rename(columns={'Rotating CB': 'Cashback'}, inplace=True)

# cashback percetnage --> variable
def convert_cashback(value):
    try:
        if isinstance(value, str) and '%' in value:
            return float(value.replace('%', '').strip()) / 100
        # base case if alr decimal
        return float(value)
    except Exception:
        return None

# convert cashback column
df['Cashback'] = df['Cashback'].apply(convert_cashback)

# keeping only necessary cols
final_columns = ['Bank Name', 'Card Name', 'Cashback', 'Spend Cap', 'url', 'image_url']
df_clean = df[final_columns]

output_file = os.path.join(output_dir, os.path.basename(input_file))
df_clean.to_csv(output_file, index=False)

print("Cleaned file saved to:", output_file)
