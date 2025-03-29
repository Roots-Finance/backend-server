import os
import sys

from dotenv import load_dotenv
from rich import print

from database import DB
from nessie import Nessie, NessieClient
from server import app

# Load environment variables
load_dotenv()
ADDR = os.getenv("API_ADDR")
PORT = os.getenv("API_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
NESSIE_KEY = os.getenv("NESSIE_KEY")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


if __name__ == "__main__":
    if not ADDR:
        ADDR = "0.0.0.0"
    if not PORT:
        PORT = 5000
    try:
        PORT = int(PORT)
    except ValueError:
        PORT = 5000
    try:
        if not DB_PORT:
            DB_PORT = 5432
        DB_PORT = int(DB_PORT)
    except ValueError:
        DB_PORT = 5432

    DB.set_url(DB_URL)
    NessieClient.set_key(NESSIE_KEY)

    print(DB_HOST)
    print(DB_URL)

    if not DB.connect():
        print("[red][!] Could not connect to database")
        sys.exit(1)
    else:
        print(f"[green][+] Connected to database '{DB_NAME}' at {DB_HOST}")

    print(f"[green][+] Running on {ADDR}:{PORT}")
    app.run(debug=True, host=ADDR, port=PORT)
