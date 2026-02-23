import os, time
from src.ssh_server import SshServer

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("./log/Pinguin-Paradis.log")
    ]
)

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    #generation over cmd: "ssh-keygen -t rsa"
    server = SshServer(os.path.expanduser('~/.ssh/id_rsa'))

    # Start the server, you can give it a custom IP address and port, or
    # leave it empty to run on 127.0.0.1:22
    #server.start("0.0.0.0", int(os.getenv("SSH_PORT", 22)))
    try:
        #print("SSH Server startet – Strg+C zum Beenden")
        logger.info("SSH Server startet – Strg+C zum Beenden")
        
        server.start("0.0.0.0", int(os.getenv("SSH_PORT", 22)))
        
        # Falls start() nicht blockiert:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt empfangen – Server wird beendet...")
        server.stop()
        #print("\nKeyboardInterrupt empfangen – Server wird beendet...")

    finally:
        server.stop()   # oder server.close(), je nach Implementierung
        logger.info("Server gestoppt.")