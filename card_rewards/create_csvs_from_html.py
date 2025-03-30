import pandas as pd
from bs4 import BeautifulSoup

# tables = ['rewards', 'gas', 'ev_charging', 'supermarket', 'wholesale_clubs',
#           'restaurant', 'drugstore', 'household_bills', 'travel', 

tables = ['supermarket']

for table in tables:
    with open(f'{table}.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    table_elem = soup.find('table')
    headers = [th.get_text(strip=True) for th in table_elem.find('thead').find_all('th')]
    card_idx = headers.index('Card Name')
    rows = table_elem.find('tbody').find_all('tr')
    urls = [row.find_all('td')[card_idx].find('a')['href'] if row.find_all('td')[card_idx].find('a') else None for row in rows]
    df = pd.read_html(html)[0]
    df['url'] = urls
    print(f"\nNow Showing: {table}.csv")
    print(df)
    df.to_csv(f'{table}.csv', index=False)
