import sqlite3
from config import DB_NAME

def setup_db():

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS firms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        industry TEXT,
        voivodeship TEXT,
        city TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        source TEXT,
        scrape_date TEXT
    )
    """)

    conn.commit()
    conn.close()

def firm_exists(c, data):

    if data.get("website"):
        c.execute(
            "SELECT id FROM firms WHERE website = ?",
            (data["website"],)
        )
        if c.fetchone():
            return True

    if data.get("phone"):
        c.execute(
            "SELECT id FROM firms WHERE phone = ?",
            (data["phone"],)
        )
        if c.fetchone():
            return True

    c.execute(
        "SELECT id FROM firms WHERE name = ? AND city = ?",
        (data.get("name"), data.get("city"))
    )

    if c.fetchone():
        return True

    return False

def save_firm(data):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if firm_exists(c, data):
        print("Duplicate skipped:", data.get("name"))
        conn.close()
        return

    print("Saving:", data.get("name"))

    c.execute("""
    INSERT INTO firms (
        name, industry, voivodeship,
        city, address, phone, email,
        website, source, scrape_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("industry"),
        data.get("voivodeship"),
        data.get("city"),
        data.get("address"),
        data.get("phone"),
        data.get("email"),
        data.get("website"),
        data.get("source"),
        data.get("scrape_date"),
    ))

    conn.commit()
    conn.close()
