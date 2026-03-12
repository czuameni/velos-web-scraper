import sqlite3
import pandas as pd
from config import DB_NAME


def export_csv():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM firms",
        conn
    )

    conn.close()

    df.to_csv("firms_export.csv", index=False)

    print("CSV exported.")
