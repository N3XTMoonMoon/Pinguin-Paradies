import sqlite3
from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor
from zope.interface import implementer
import datetime

#############################
# DATABASE INITIALISIERUNG #
#############################

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER NOT NULL,
        price REAL NOT NULL
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

init_db()

#############################
# SSH PROTOKOLL
#############################

class SSHPinguinProtocol(recvline.HistoricRecvLine):

    def __init__(self, user):
        self.user = user
        self.state = "HOME"
        self.current_order = []
        self.customer_id = None

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("🐧 Willkommen im Pinguin Restaurant System")
        self.terminal.nextLine()
        self.show_home()

    def showPrompt(self):
        self.terminal.write("\n$ ")

    #############################
    # HOME SCREEN
    #############################

    def show_home(self):
        self.state = "HOME"
        self.terminal.write("\n--- HOME ---")
        self.terminal.nextLine()
        self.terminal.write("1 -> Bestellen")
        self.terminal.nextLine()
        self.terminal.write("2 -> Einlagern")
        self.terminal.nextLine()
        self.terminal.write("3 -> Inventar anzeigen")
        self.terminal.nextLine()
        self.terminal.write("4 -> Umsätze anzeigen")
        self.terminal.nextLine()
        self.terminal.write("quit -> Logout")
        self.terminal.nextLine()
        self.showPrompt()

    #############################
    # INPUT HANDLER
    #############################

    def lineReceived(self, line):
        line = line.decode().strip()

        if self.state == "HOME":
            self.handle_home(line)
        elif self.state == "BESTELLUNG_CUSTOMER":
            self.customer_id = line if line else None
            self.show_items()
        elif self.state == "BESTELLUNG_ITEM":
            self.handle_item_selection(line)
        elif self.state == "BESTELLUNG_MENGE":
            self.handle_quantity(line)
        elif self.state == "EINLAGERN":
            self.handle_stock(line)
        else:
            self.show_home()

    def handle_home(self, line):
        if line == "1":
            self.start_order()
        elif line == "2":
            self.start_stock()
        elif line == "3":
            self.show_inventory()
        elif line == "4":
            self.show_revenue()
        elif line == "quit":
            self.terminal.loseConnection()
        else:
            self.terminal.write("Ungültige Auswahl!")
            self.terminal.nextLine()
            self.show_home()

    #############################
    # BESTELLUNG
    #############################

    def start_order(self):
        self.current_order = []
        self.terminal.write("Kundennummer eingeben (optional, Enter = überspringen):")
        self.terminal.nextLine()
        self.state = "BESTELLUNG_CUSTOMER"

    def show_items(self):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id, name, price, stock FROM inventory WHERE stock > 0")
        items = c.fetchall()
        conn.close()

        self.terminal.write("\n--- Verfügbare Gerichte ---")
        self.terminal.nextLine()

        for item in items:
            self.terminal.write(f"{item[0]} - {item[1]} | {item[2]}€ | Lager: {item[3]}")
            self.terminal.nextLine()

        self.terminal.write("\nArtikel-ID wählen oder 'fertig'")
        self.terminal.nextLine()
        self.state = "BESTELLUNG_ITEM"

    def handle_item_selection(self, line):
        if line.lower() == "fertig":
            self.finish_order()
            return

        if not line.isdigit():
            self.terminal.write("Bitte gültige Artikel-ID eingeben!")
            self.terminal.nextLine()
            return

        self.selected_item = int(line)
        self.terminal.write("Menge eingeben:")
        self.terminal.nextLine()
        self.state = "BESTELLUNG_MENGE"

    def handle_quantity(self, line):
        if not line.isdigit():
            self.terminal.write("Bitte gültige Menge eingeben!")
            self.terminal.nextLine()
            return

        quantity = int(line)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT price, stock FROM inventory WHERE id=?", (self.selected_item,))
        item = c.fetchone()

        if not item:
            self.terminal.write("Artikel existiert nicht!")
            self.terminal.nextLine()
        elif item[1] < quantity:
            self.terminal.write("Nicht genügend Lagerbestand!")
            self.terminal.nextLine()
        else:
            self.current_order.append((self.selected_item, quantity, item[0]))
            c.execute("UPDATE inventory SET stock = stock - ? WHERE id=?", (quantity, self.selected_item))
            conn.commit()
            self.terminal.write("Artikel hinzugefügt!")
            self.terminal.nextLine()

        conn.close()
        self.show_items()

    def finish_order(self):
        total = sum(q * price for (_, q, price) in self.current_order)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO orders (customer_id, total, created_at) VALUES (?, ?, ?)",
                  (self.customer_id, total, str(datetime.datetime.now())))
        order_id = c.lastrowid

        for item_id, quantity, price in self.current_order:
            c.execute("INSERT INTO order_items VALUES (?, ?, ?)",
                      (order_id, item_id, quantity))

        conn.commit()
        conn.close()

        self.terminal.write(f"\nBestellung abgeschlossen! Gesamtbetrag: {total:.2f}€")
        self.terminal.nextLine()
        self.show_home()

    #############################
    # EINLAGERN MIT VALIDIERUNG
    #############################

    def start_stock(self):
        self.state = "EINLAGERN"
        self.terminal.write("Artikel-ID und Menge eingeben (z.B. 3 10)")
        self.terminal.nextLine()

    def handle_stock(self, line):
        parts = line.split()

        if len(parts) != 2:
            self.terminal.write("FEHLER: Bitte ID und Menge angeben! Beispiel: 3 10")
            self.terminal.nextLine()
            return

        if not parts[0].isdigit() or not parts[1].isdigit():
            self.terminal.write("FEHLER: Nur Zahlen erlaubt!")
            self.terminal.nextLine()
            return

        item_id = int(parts[0])
        quantity = int(parts[1])

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT name FROM inventory WHERE id=?", (item_id,))
        item = c.fetchone()

        if not item:
            self.terminal.write("Artikel-ID existiert nicht!")
        else:
            c.execute("UPDATE inventory SET stock = stock + ? WHERE id=?", (quantity, item_id))
            conn.commit()
            self.terminal.write(f"{quantity}x {item[0]} erfolgreich eingelagert!")

        conn.close()
        self.terminal.nextLine()
        self.show_home()

    #############################
    # INVENTAR
    #############################

    def show_inventory(self):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id, name, stock, price FROM inventory")
        items = c.fetchall()
        conn.close()

        self.terminal.write("\n--- INVENTAR ---")
        self.terminal.nextLine()

        for i in items:
            self.terminal.write(f"{i[0]} | {i[1]} | Lager: {i[2]} | Preis: {i[3]}€")
            self.terminal.nextLine()

        self.show_home()
        
    #############################
    # UMSÄTZE
    #############################

    def show_revenue(self):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT SUM(total) FROM orders")
        total = c.fetchone()[0]
        conn.close()

        self.terminal.write(f"\nGesamtumsatz: {total if total else 0}€")
        self.terminal.nextLine()
        self.show_home()


#############################
# SSH INFRASTRUKTUR
#############################

@implementer(ISession)
class SSHPinguinAvatar(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({b'session': session.SSHSession})

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHPinguinProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError()

    def closed(self):
        pass


@implementer(portal.IRealm)
class SSHPinguinRealm(object):

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], SSHPinguinAvatar(avatarId.decode()), lambda: None
        raise NotImplementedError()


def getRSAKeys(sshFactory):
    privateKey = keys.Key.fromFile("id_ed25519")
    publicKey = privateKey.public()

    sshFactory.privateKeys = {b"ssh-ed25519": privateKey}
    sshFactory.publicKeys = {b"ssh-ed25519": publicKey}
    return sshFactory


if __name__ == "__main__":
    sshFactory = factory.SSHFactory()
    sshFactory.portal = portal.Portal(SSHPinguinRealm())

    users = {'admin': b'admin', 'service': b'service'}
    sshFactory.portal.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

    sshFactory = getRSAKeys(sshFactory)

    reactor.listenTCP(2222, sshFactory)
    reactor.run()