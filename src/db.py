import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS Artikel (
        ARTIKELNUMMER INTEGER PRIMARY KEY AUTOINCREMENT,
        BEZEICHNUNG TEXT NOT NULL,
        BESCHREIBUNG TEXT NOT NULL,
        PREISBERECHNUNG TEXT NOT NULL,
        
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        total REAL,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_id INTEGER,
        item_id INTEGER,
        quantity INTEGER
    )
    """)

    # Seed Daten (nur wenn leer)
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        items = [
            ("Fischburger Deluxe", 20, 7.50),
            ("Eisberg-Salat", 15, 5.20),
            ("Krabben-Knusper Menü", 10, 9.90),
            ("Antarktis Nuggets", 30, 6.40),
            ("Polar Pommes", 40, 3.50),
            ("Walross Shake", 25, 4.80)
        ]
        c.executemany("INSERT INTO inventory (name, stock, price) VALUES (?, ?, ?)", items)

    conn.commit()
    conn.close()

def get_all_available_stock():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM inventory WHERE stock > 0")
    items = c.fetchall()
    conn.close()
    return items

def get_price_and_stock_by_item_id(selected_item_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT price, stock FROM inventory WHERE id=?", selected_item_id)
    item = c.fetchone()
    return item