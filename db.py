import sqlite3
import datetime

DB_NAME = "database.db"
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE PreisTabelle (
        Preis_ID INTEGER PRIMARY KEY,
        Artikel_ID INTEGER,
        Preis VARCHAR(255),
        StartDatum DATE,
        EndDatum DATE
    )
    """)

    # Artikel
    c.execute("""
    CREATE TABLE Artikel (
        Artikel_ID INTEGER PRIMARY KEY,
        Bezeichnung VARCHAR(255),
        Beschreibung TEXT
    )
    """)

    c.execute("""
    CREATE TABLE Rezept (
        Rezept_ID INTEGER PRIMARY KEY,
        Dauer INTEGER,
        Preis_Verkauf INTEGER,
        Kalorien INTEGER,
        Anleitung_ID INTEGER,
        Zutaten_ID INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE Anleitungen (
        Anleitung_ID INTEGER PRIMARY KEY,
        Schritt INTEGER,
        Text VARCHAR(255)
    )
    """)

    c.execute("""
    CREATE TABLE Zutaten_Position (
        Artikel_ID INTEGER PRIMARY KEY,
        Rezept_ID INTEGER,
        Menge INTEGER,
        Menge_Einheit VARCHAR(255)
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Lager (
        Lager_ID INTEGER PRIMARY KEY,
        Restaurant_ID INTEGER,
        Zusatz VARCHAR
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Lager_Bestand (
        Lager_ID INTEGER,
        Artikel_ID INTEGER,
        Bestand INTEGER,
        PRIMARY KEY (Lager_ID, Artikel_ID)
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Tisch (
        Tisch_ID INTEGER PRIMARY KEY,
        Restaurant_ID INTEGER
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Restaurant (
        Restaurant_ID INTEGER PRIMARY KEY,
        Adresse VARCHAR
    )
    """)

    # Mitarbeiter
    c.execute("""
    CREATE TABLE Mitarbeiter (
        Mitarbeiter_ID INTEGER PRIMARY KEY,
        Vorname VARCHAR(100),
        Nachname VARCHAR(100),
        Position VARCHAR(100),
        HRStatus VARCHAR(50)
    )
    """)

    # Bestellung
    c.execute("""
    CREATE TABLE Bestellung (
        Bestellung_ID INTEGER PRIMARY KEY,
        Kunde_ID INTEGER,
        BestellDatum DATE,
        AbholStatus VARCHAR(50),
        Rechnung_ID INTEGER,
        FOREIGN KEY (Kunde_ID) REFERENCES Kunde(Kunde_ID)
    )
    """)

    # Bestellposition (n:m Beziehung Bestellung <-> Artikel)
    c.execute("""
    CREATE TABLE Bestellposition (
        Bestellposition_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Bestell_ID INTEGER,
        Artikel_ID INTEGER,
        Menge INTEGER,
        Preis INTEGER,
        FOREIGN KEY (Bestell_ID) REFERENCES Bestellung(Bestellung_ID),
        FOREIGN KEY (Artikel_ID) REFERENCES Artikel(Artikel_ID)
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Kunde (
        Kunde_ID INTEGER PRIMARY KEY,
        KundenName VARCHAR(255),
        KundenVorname VARCHAR(255),
        Adresse VARCHAR(255),
        TelefonNummer VARCHAR(255),
        E_Mail VARCHAR(255)
    )
    """)

    # Kunde
    c.execute("""
    CREATE TABLE Rechnung (
        Rechnung_ID INTEGER PRIMARY KEY,
        Kunde_ID INTEGER,
        Datum DATE,
        Betrag INTEGER,
        MwStSatz INTEGER,
        BezahlStatus VARCHAR
    )
    """)

    # Mitarbeiter
    c.execute("""
    CREATE TABLE Passwort (
        Mitarbeiter_ID INTEGER PRIMARY KEY,
        Passwort VARCHAR(200)
    )
    """)

    # Mitarbeiter
    c.execute("""
    CREATE TABLE RestaurantMitarbeiter (
        Mitarbeiter_ID INTEGER PRIMARY KEY,
        Restaurant_ID INTEGER
    )
    """)

    # Seed Daten (nur wenn leer)
    c.execute("SELECT COUNT(*) FROM Artikel")
    if c.fetchone()[0] == 0:
        items = [
            ("Fischburger Deluxe", 20, 7.50),
            ("Eisberg-Salat", 15, 5.20),
            ("Krabben-Knusper Menü", 10, 9.90),
            ("Antarktis Nuggets", 30, 6.40),
            ("Polar Pommes", 40, 3.50),
            ("Walross Shake", 25, 4.80)
        ]
        #c.executemany("INSERT INTO Artikel (name, stock, price) VALUES (?, ?, ?)", items)

    conn.commit()
    conn.close()

def fill_with_test_data():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.executemany("""
    INSERT INTO Artikel (Artikel_ID, Bezeichnung, Beschreibung)
    VALUES (?, ?, ?)
    """, [
        # Zutaten
        (1, "Fischfilet", "Frischer Fisch aus der Antarktis"),
        (2, "Eisbergsalat", "Knackiger Salat"),
        (3, "Kartoffeln", "Für Pommes geeignet"),
        (4, "Krabben", "Kleine Meeresfrüchte"),
        (5, "Milch", "Für Shakes"),
        (6, "Zucker", "Süßungsmittel"),

        # Gerichte
        (100, "Fischburger Deluxe", "Burger mit Fischfilet"),
        (101, "Krabben-Knusper Menü", "Knusprige Krabben mit Beilage"),
        (102, "Polar Pommes", "Knusprige Pommes"),
        (103, "Walross Shake", "Süßer Milchshake"),
        (104, "Eisberg-Salat Bowl", "Frischer Salatmix")
    ])

    c.executemany("""
    INSERT INTO PreisTabelle (Preis_ID, Artikel_ID, Preis, StartDatum, EndDatum)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 1, "2.50", "2026-01-01", "2026-12-31"),
        (2, 2, "1.20", "2026-01-01", "2026-12-31"),
        (3, 3, "0.80", "2026-01-01", "2026-12-31"),
        (4, 4, "3.00", "2026-01-01", "2026-12-31"),
        (5, 5, "1.00", "2026-01-01", "2026-12-31"),
        (6, 6, "0.50", "2026-01-01", "2026-12-31"),

        # Gerichte
        (10, 100, "7.50", "2026-01-01", "2026-12-31"),
        (11, 101, "9.90", "2026-01-01", "2026-12-31"),
        (12, 102, "3.50", "2026-01-01", "2026-12-31"),
        (13, 103, "4.80", "2026-01-01", "2026-12-31"),
        (14, 104, "5.20", "2026-01-01", "2026-12-31")
    ])
    
    c.executemany("""
    INSERT INTO Lager (Lager_ID, Restaurant_ID, Zusatz)
    VALUES (?, ?, ?)
    """, [
        (1, 1, "Hauptlager"),
        (2, 1, "Kühlhaus")
    ])
    
    c.executemany("""
    INSERT INTO Lager_Bestand (Lager_ID, Artikel_ID, Bestand)
    VALUES (?, ?, ?)
    """, [
        (1, 1, 50),
        (1, 2, 40),
        (1, 3, 100),
        (1, 4, 30),
        (2, 5, 60),
        (2, 6, 80)
    ])
    
    c.execute("""
    INSERT INTO Restaurant (Restaurant_ID, Adresse)
    VALUES (1, "Antarktis - Sektor 7, Iglu 3")
    """)
    
    c.executemany("""
    INSERT INTO Mitarbeiter (Mitarbeiter_ID, Vorname, Nachname, Position, HRStatus)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "Pingo", "Chef", "Koch", "Aktiv"),
        (2, "Lola", "Flosse", "Service", "Aktiv"),
        (3, "Kalle", "Eisfuß", "Manager", "Aktiv")
    ])
    
    c.executemany("""
    INSERT INTO Kunde (Kunde_ID, KundenName, KundenVorname, Adresse, TelefonNummer, E_Mail)
    VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, "Frost", "Olaf", "Eisberg 1", "123456", "olaf@ice.de"),
        (2, "Schnee", "Anna", "Gletscher 2", "654321", "anna@ice.de")
    ])
    
    c.execute("""
    INSERT INTO Bestellung (Bestellung_ID, Kunde_ID, BestellDatum, AbholStatus, Rechnung_ID)
    VALUES (1, 1, "2026-03-30", "offen", 1)
    """)
    conn.commit()
    conn.close()
    




def get_connection():
    return sqlite3.connect(DB_NAME)


# 🔎 Artikel inkl. Preis + Bestand
def get_all_available_stock():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            a.Artikel_ID,
            a.Bezeichnung,
            COALESCE(p.Preis, 0),
            COALESCE(lb.Bestand, 0)
        FROM Artikel a
        LEFT JOIN PreisTabelle p ON a.Artikel_ID = p.Artikel_ID
        LEFT JOIN Lager_Bestand lb ON a.Artikel_ID = lb.Artikel_ID
        WHERE lb.Bestand > 0
    """)

    result = c.fetchall()
    conn.close()
    return result


# 🔎 Preis + Bestand
def get_price_and_stock_by_item_id(item_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            COALESCE(p.Preis, 0),
            COALESCE(lb.Bestand, 0)
        FROM Artikel a
        LEFT JOIN PreisTabelle p ON a.Artikel_ID = p.Artikel_ID
        LEFT JOIN Lager_Bestand lb ON a.Artikel_ID = lb.Artikel_ID
        WHERE a.Artikel_ID = ?
    """, (item_id,))

    result = c.fetchone()
    conn.close()
    return result


# 🔽 Bestand reduzieren
def reduce_stock(item_id, quantity):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE Lager_Bestand
        SET Bestand = Bestand - ?
        WHERE Artikel_ID = ?
    """, (quantity, item_id))

    conn.commit()
    conn.close()


# 🔼 Bestand erhöhen
def increase_stock(item_id, quantity):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE Lager_Bestand
        SET Bestand = Bestand + ?
        WHERE Artikel_ID = ?
    """, (quantity, item_id))

    conn.commit()
    conn.close()


# 🧾 Bestellung speichern
def create_order(customer_id, total):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO Bestellung (Kunde_ID, BestellDatum, AbholStatus)
        VALUES (?, ?, ?)
    """, (customer_id, str(datetime.datetime.now()), "offen"))

    order_id = c.lastrowid

    conn.commit()
    conn.close()

    return order_id


# 🍽️ Bestellposition speichern
def add_order_item(order_id, artikel_id, menge, preis):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO Bestellposition (Bestell_ID, Artikel_ID, Menge, Preis)
        VALUES (?, ?, ?, ?)
    """, (order_id, artikel_id, menge, preis))

    conn.commit()
    conn.close()


# 💰 Umsatz berechnen
def get_total_revenue():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT SUM(Menge * Preis) FROM Bestellposition
    """)

    result = c.fetchone()[0]
    conn.close()

    return result if result else 0


# 📦 Inventar anzeigen
def get_full_inventory():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            a.Artikel_ID,
            a.Bezeichnung,
            COALESCE(lb.Bestand, 0),
            COALESCE(p.Preis, 0)
        FROM Artikel a
        LEFT JOIN Lager_Bestand lb ON a.Artikel_ID = lb.Artikel_ID
        LEFT JOIN PreisTabelle p ON a.Artikel_ID = p.Artikel_ID
    """)

    result = c.fetchall()
    conn.close()
    return result