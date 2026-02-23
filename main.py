from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor
from zope.interface import implementer
 
class SSHDemoProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
       self.user = user
 
    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Welcome to my test SSH server.")
        self.terminal.nextLine()
        self.do_help()
        self.showPrompt()
 
    def showPrompt(self):
        self.terminal.write("$ ")
 
    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd.decode("utf-8"), None)
 
    def lineReceived(self, line):
        line = line.strip()
        if line:
            print(line)
            f = open('logfile.log', 'w')
            f.write(line.decode("utf-8"))
            f.close
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception as e:
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
            else:
                self.terminal.write("No such command.")
                self.terminal.nextLine()
        self.showPrompt()
 
    def do_help(self):
        publicMethods = filter(
            lambda funcname: funcname.startswith('do_'), dir(self))
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        self.terminal.write("Commands: " + " ".join(commands))
        self.terminal.nextLine()
 
    def do_echo(self, *args):
        self.terminal.write(" ".join(args))
        self.terminal.nextLine()
 
    def do_whoami(self):
        self.terminal.write(self.user.username)
        self.terminal.nextLine()
 
    def do_quit(self):
        self.terminal.write("Thanks for playing!")
        self.terminal.nextLine()
        self.terminal.loseConnection()
 
    def do_clear(self):
        self.terminal.reset()
        
    def do_test(self):
        self.terminal.write('Test')
        self.terminal.nextLine()
 
@implementer(ISession)
class SSHDemoAvatar(avatar.ConchUser):
 
 
    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({b'session': session.SSHSession})
 
 
    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHDemoProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))
 
 
    def getPty(self, terminal, windowSize, attrs):
        return None
 
 
    def execCommand(self, protocol, cmd):
        raise NotImplementedError()
 
    def closed(self):
        pass
 
@implementer(portal.IRealm)
class SSHDemoRealm(object):
     
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], SSHDemoAvatar(avatarId), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found.")
def getRSAKeys():
    privateKey = keys.Key.fromFile("id_rsa")
    publicKey = privateKey.public()

    sshFactory.privateKeys = {
        b"ssh-rsa": privateKey
    }

    sshFactory.publicKeys = {
        b"ssh-rsa": publicKey
    }
    return sshFactory
 
if __name__ == "__main__":
    sshFactory = factory.SSHFactory()
    sshFactory.portal = portal.Portal(SSHDemoRealm())
 

sshFactory = getRSAKeys()
users = {'admin': b'admin', 'guest': b'bbb'}
sshFactory.portal.registerChecker(
    checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

reactor.listenTCP(22, sshFactory)
reactor.run()