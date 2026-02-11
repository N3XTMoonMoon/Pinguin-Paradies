import paramiko
import logging

from src.server_base import ServerBase
from src.ssh_server_interface import SshServerInterface
from src.shell import Shell

logger = logging.getLogger(__name__)

class SshServer(ServerBase):

    def __init__(self, host_key_file, host_key_file_password=None):
        super(SshServer, self).__init__()

        self._host_key = paramiko.RSAKey.from_private_key_file(host_key_file, host_key_file_password)

    def connection_function(self, client):
        try:
            logger.info("New client connected")

            transport = paramiko.Transport(client)
            transport.add_server_key(self._host_key)

            server = SshServerInterface()
            transport.start_server(server=server)

            channel = transport.accept(20)
            if channel is None:
                logger.warning("No channel")
                return

            logger.info("Channel opened")

            channel.send(b"\r\nCustom SSH Shell\r\n")
            channel.send(b"P-Paradise> ")

            bufferedCommand = ''

            while True:
                data = channel.recv(1024)
                if not data:
                    break

                command = data.decode("utf-8")
                
                if command in ("\r"):
                    logger.info('COMMAND \\r ENTER')

                #turn on for logging of every keyinput
                logger.debug(f"Received command: {command}")
                if(command == "\r"):
                    
                
                    channel.send("\r\n")
                    #overwrite comand for validation
                    command = bufferedCommand
                    #reset buffer
                    bufferedCommand = ''
                    if command == "logout":
                        channel.send(b"See you later!\r\n")
                        break
                    elif command.startswith("greet"):
                        parts = command.split()
                        if len(parts) > 1:
                            channel.send(f"Hey {parts[1]}!\r\n".encode())
                        else:
                            channel.send(b"Hello there!\r\n")
                    else:
                        channel.send(f"Unbekannter Befehl: '{command}'\r\n".encode())

                    channel.send(b"P-Paradise> ")
                else:
                    bufferedCommand += command
                    channel.send(command)

            channel.close()
            transport.close()
            logger.info("Connection closed")

        except Exception:
            logger.exception("SSH Error")
