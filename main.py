
from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor
from zope.interface import implementer
import datetime

from db import (
    init_db,
    fill_with_test_data,
    get_all_available_stock,
    get_price_and_stock_by_item_id,
    reduce_stock,
    increase_stock,
    create_order,
    add_order_item,
    get_total_revenue,
    get_full_inventory
)
# Datenbankerstellung

init_db()

fill_with_test_data()

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
        items = get_all_available_stock()

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
        item = get_price_and_stock_by_item_id(self.selected_item)

        if not item:
            self.terminal.write("Artikel existiert nicht!")
        elif item[1] < quantity:
            self.terminal.write("Nicht genügend Lagerbestand!")
        else:
            self.current_order.append((self.selected_item, quantity, float(item[0])))
            reduce_stock(self.selected_item, quantity)

            self.terminal.write("Artikel hinzugefügt!")

        self.terminal.nextLine()
        self.show_items()

    def finish_order(self):
        total = sum(q * price for (_, q, price) in self.current_order)

        order_id = create_order(self.customer_id, total)

        for item_id, quantity, price in self.current_order:
            add_order_item(order_id, item_id, quantity, price)

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
            self.terminal.write("FEHLER: Beispiel: 3 10")
            self.terminal.nextLine()
            return

        if not parts[0].isdigit() or not parts[1].isdigit():
            self.terminal.write("FEHLER: Nur Zahlen!")
            self.terminal.nextLine()
            return

        item_id = int(parts[0])
        quantity = int(parts[1])

        item = get_price_and_stock_by_item_id(item_id)

        if not item:
            self.terminal.write("Artikel existiert nicht!")
        else:
            increase_stock(item_id, quantity)
            self.terminal.write(f"{quantity} Stück erfolgreich eingelagert!")

        self.terminal.nextLine()
        self.show_home()

    #############################
    # INVENTAR
    #############################

    def show_inventory(self):
        items = get_full_inventory()

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
        total = get_total_revenue()

        self.terminal.write(f"\nGesamtumsatz: {total:.2f}€")
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

    reactor.listenTCP(22, sshFactory)
    reactor.run()